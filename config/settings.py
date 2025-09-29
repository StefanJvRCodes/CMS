"""Configuration settings for the CMS application."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # RabbitMQ Configuration
    rabbitmq_url: str = "amqp://cms_user:cms_password@localhost:5672/cms_vhost"
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "cms_user"
    rabbitmq_password: str = "cms_password"
    rabbitmq_vhost: str = "cms_vhost"
    
    # n8n Configuration
    n8n_webhook_url: str = "http://localhost:5678/webhook"
    n8n_api_url: str = "http://localhost:5678/api"
    
    # Application Configuration
    app_name: str = "CMS Event-Driven System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Event Configuration
    default_exchange: str = "cms_events"
    default_queue: str = "cms_queue"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()