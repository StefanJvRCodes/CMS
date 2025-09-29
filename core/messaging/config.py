"""
RabbitMQ Configuration Module
Manages RabbitMQ connection settings and configuration
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class RabbitMQConfig:
    """RabbitMQ connection configuration"""
    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"
    connection_timeout: int = 30
    heartbeat: int = 600
    
    @classmethod
    def from_env(cls) -> 'RabbitMQConfig':
        """Create configuration from environment variables"""
        return cls(
            host=os.getenv('RABBITMQ_HOST', 'localhost'),
            port=int(os.getenv('RABBITMQ_PORT', '5672')),
            username=os.getenv('RABBITMQ_USERNAME', 'guest'),
            password=os.getenv('RABBITMQ_PASSWORD', 'guest'),
            virtual_host=os.getenv('RABBITMQ_VHOST', '/'),
            connection_timeout=int(os.getenv('RABBITMQ_CONNECTION_TIMEOUT', '30')),
            heartbeat=int(os.getenv('RABBITMQ_HEARTBEAT', '600'))
        )
    
    def get_connection_url(self) -> str:
        """Get RabbitMQ connection URL"""
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}{self.virtual_host}"


# Default configuration instance
config = RabbitMQConfig.from_env()