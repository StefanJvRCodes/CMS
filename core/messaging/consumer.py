"""
RabbitMQ Fanout Consumer
Consumes messages from fanout exchanges
"""
import json
import logging
from typing import Callable, Optional, Any, Dict
import pika

from .connection import RabbitMQConnection
from .config import RabbitMQConfig

logger = logging.getLogger(__name__)


class FanoutConsumer:
    """Consumer for fanout exchanges in RabbitMQ"""
    
    def __init__(self, 
                 exchange_name: str, 
                 queue_name: Optional[str] = None,
                 config: Optional[RabbitMQConfig] = None):
        self.exchange_name = exchange_name
        self.queue_name = queue_name or f"{exchange_name}_queue"
        self.connection = RabbitMQConnection(config)
        self._setup_complete = False
        self._consuming = False
    
    def setup_queue(self) -> str:
        """
        Declare the fanout exchange and bind a queue to it
        
        Returns:
            str: The actual queue name (useful for auto-generated names)
        """
        try:
            with self.connection.channel_context() as channel:
                # Declare the fanout exchange
                channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type='fanout',
                    durable=True
                )
                
                # Declare the queue (let RabbitMQ generate name if not specified)
                if self.queue_name:
                    result = channel.queue_declare(queue=self.queue_name, durable=True)
                    actual_queue_name = self.queue_name
                else:
                    # Auto-generate exclusive queue name
                    result = channel.queue_declare(queue='', exclusive=True)
                    actual_queue_name = result.method.queue
                    self.queue_name = actual_queue_name
                
                # Bind queue to exchange
                channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=actual_queue_name
                )
                
                self._setup_complete = True
                logger.info(f"Queue '{actual_queue_name}' bound to fanout exchange '{self.exchange_name}'")
                return actual_queue_name
                
        except Exception as e:
            logger.error(f"Failed to setup queue for exchange '{self.exchange_name}': {e}")
            raise
    
    def consume_messages(self, 
                        callback: Callable[[Dict[str, Any]], None],
                        auto_ack: bool = False) -> None:
        """
        Start consuming messages from the queue
        
        Args:
            callback: Function to handle received messages
            auto_ack: Whether to automatically acknowledge messages
        """
        if not self._setup_complete:
            self.setup_queue()
        
        def message_handler(ch, method, properties, body):
            """Internal message handler"""
            try:
                # Try to parse JSON, fallback to string
                try:
                    message_data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    message_data = body.decode('utf-8')
                
                # Create message info
                message_info = {
                    'data': message_data,
                    'exchange': method.exchange,
                    'routing_key': method.routing_key,
                    'delivery_tag': method.delivery_tag,
                    'properties': {
                        'content_type': properties.content_type,
                        'timestamp': properties.timestamp,
                        'message_id': properties.message_id,
                    }
                }
                
                # Call the user callback
                callback(message_info)
                
                # Acknowledge message if not auto-ack
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                logger.debug(f"Processed message from exchange '{self.exchange_name}'")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Reject message and requeue on error
                if not auto_ack:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        try:
            with self.connection.channel_context() as channel:
                # Set QoS to process one message at a time
                channel.basic_qos(prefetch_count=1)
                
                # Start consuming
                channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=message_handler,
                    auto_ack=auto_ack
                )
                
                self._consuming = True
                logger.info(f"Started consuming from queue '{self.queue_name}' on exchange '{self.exchange_name}'")
                logger.info("Waiting for messages. To exit press CTRL+C")
                
                # Start consuming (blocking)
                channel.start_consuming()
                
        except KeyboardInterrupt:
            logger.info("Consumption interrupted by user")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error during message consumption: {e}")
            raise
    
    def stop_consuming(self) -> None:
        """Stop consuming messages"""
        if self._consuming:
            try:
                with self.connection.channel_context() as channel:
                    channel.stop_consuming()
                self._consuming = False
                logger.info("Stopped consuming messages")
            except Exception as e:
                logger.error(f"Error stopping consumption: {e}")
    
    def close(self) -> None:
        """Close the connection"""
        self.stop_consuming()
        self.connection.disconnect()
    
    def __enter__(self):
        self.setup_queue()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()