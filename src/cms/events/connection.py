"""RabbitMQ connection management for the CMS system."""
import json
import logging
from typing import Optional, Callable, Any
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from config.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """Manages RabbitMQ connection and basic operations."""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None
        self._is_connected = False
    
    def connect(self) -> bool:
        """Establish connection to RabbitMQ."""
        try:
            connection_params = pika.URLParameters(settings.rabbitmq_url)
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            self._is_connected = True
            
            # Declare the default exchange and queue
            self.setup_default_infrastructure()
            
            logger.info("Successfully connected to RabbitMQ")
            return True
            
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self._is_connected = False
            return False
    
    def setup_default_infrastructure(self):
        """Set up default exchanges and queues."""
        if not self.channel:
            return
        
        try:
            # Declare exchange
            self.channel.exchange_declare(
                exchange=settings.default_exchange,
                exchange_type='topic',
                durable=True
            )
            
            # Declare default queue
            self.channel.queue_declare(
                queue=settings.default_queue,
                durable=True
            )
            
            # Bind queue to exchange with wildcard routing key
            self.channel.queue_bind(
                exchange=settings.default_exchange,
                queue=settings.default_queue,
                routing_key='#'
            )
            
            logger.info("Default RabbitMQ infrastructure set up successfully")
            
        except AMQPChannelError as e:
            logger.error(f"Failed to set up RabbitMQ infrastructure: {e}")
    
    def disconnect(self):
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self._is_connected = False
            logger.info("Disconnected from RabbitMQ")
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._is_connected and self.connection and not self.connection.is_closed
    
    def publish_message(self, message: dict, routing_key: str, exchange: str = None) -> bool:
        """Publish a message to RabbitMQ."""
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            exchange = exchange or settings.default_exchange
            
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published message to {exchange}/{routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
    def consume_messages(self, queue: str, callback: Callable[[Any, Any, Any, bytes], None]) -> bool:
        """Start consuming messages from a queue."""
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info(f"Started consuming messages from queue: {queue}")
            self.channel.start_consuming()
            return True
            
        except Exception as e:
            logger.error(f"Failed to consume messages: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Global connection instance
rabbitmq_connection = RabbitMQConnection()