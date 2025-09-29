"""
RabbitMQ Connection Manager
Handles connection lifecycle and channel management
"""
import logging
import pika
from typing import Optional
from contextlib import contextmanager

from .config import RabbitMQConfig, config as default_config

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """Manages RabbitMQ connection and channels"""
    
    def __init__(self, config: Optional[RabbitMQConfig] = None):
        self.config = config or default_config
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
    
    def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.virtual_host,
                credentials=pika.PlainCredentials(
                    self.config.username,
                    self.config.password
                ),
                connection_attempts=3,
                retry_delay=1,
                socket_timeout=self.config.connection_timeout,
                heartbeat=self.config.heartbeat
            )
            
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            logger.info(f"Connected to RabbitMQ at {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close RabbitMQ connection"""
        try:
            if self._channel and self._channel.is_open:
                self._channel.close()
                logger.debug("Channel closed")
            
            if self._connection and self._connection.is_open:
                self._connection.close()
                logger.info("Connection closed")
                
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def get_channel(self) -> pika.channel.Channel:
        """Get the active channel, connecting if necessary"""
        if not self._connection or self._connection.is_closed:
            self.connect()
        
        if not self._channel or self._channel.is_closed:
            self._channel = self._connection.channel()
        
        return self._channel
    
    @contextmanager
    def channel_context(self):
        """Context manager for channel operations"""
        try:
            channel = self.get_channel()
            yield channel
        except Exception as e:
            logger.error(f"Error in channel context: {e}")
            raise
        finally:
            # Keep connection alive, just ensure proper cleanup
            pass
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()