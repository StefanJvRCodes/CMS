"""
RabbitMQ Fanout Producer
Publishes messages to fanout exchanges
"""
import json
import logging
from typing import Any, Dict, Optional
import pika

from .connection import RabbitMQConnection
from .config import RabbitMQConfig

logger = logging.getLogger(__name__)


class FanoutProducer:
    """Producer for fanout exchanges in RabbitMQ"""
    
    def __init__(self, exchange_name: str, config: Optional[RabbitMQConfig] = None):
        self.exchange_name = exchange_name
        self.connection = RabbitMQConnection(config)
        self._setup_complete = False
    
    def setup_exchange(self) -> None:
        """Declare the fanout exchange"""
        try:
            with self.connection.channel_context() as channel:
                channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type='fanout',
                    durable=True
                )
                self._setup_complete = True
                logger.info(f"Fanout exchange '{self.exchange_name}' declared successfully")
        except Exception as e:
            logger.error(f"Failed to setup exchange '{self.exchange_name}': {e}")
            raise
    
    def publish_message(self, message: Any, properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a message to the fanout exchange
        
        Args:
            message: The message to publish (will be JSON serialized)
            properties: Optional message properties
            
        Returns:
            bool: True if message was published successfully
        """
        if not self._setup_complete:
            self.setup_exchange()
        
        try:
            # Serialize message to JSON
            if isinstance(message, (dict, list)):
                body = json.dumps(message)
            elif isinstance(message, str):
                body = message
            else:
                body = json.dumps(str(message))
            
            # Prepare message properties
            msg_properties = pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json',
                timestamp=None,
                **(properties or {})
            )
            
            with self.connection.channel_context() as channel:
                channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key='',  # Fanout ignores routing key
                    body=body,
                    properties=msg_properties
                )
                
                logger.debug(f"Published message to exchange '{self.exchange_name}': {body[:100]}...")
                return True
                
        except Exception as e:
            logger.error(f"Failed to publish message to exchange '{self.exchange_name}': {e}")
            return False
    
    def publish_dict(self, data: Dict[str, Any], **kwargs) -> bool:
        """Convenience method to publish dictionary data"""
        return self.publish_message(data, **kwargs)
    
    def publish_text(self, text: str, **kwargs) -> bool:
        """Convenience method to publish text messages"""
        return self.publish_message(text, **kwargs)
    
    def close(self) -> None:
        """Close the connection"""
        self.connection.disconnect()
    
    def __enter__(self):
        self.setup_exchange()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()