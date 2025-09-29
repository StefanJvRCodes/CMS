#!/usr/bin/env python3
"""
Basic test script for the messaging module
Tests configuration and class instantiation without requiring RabbitMQ server
"""
import os
import logging
import tempfile

from core.messaging import RabbitMQConfig, FanoutProducer, FanoutConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_config():
    """Test configuration functionality"""
    logger.info("Testing RabbitMQConfig...")
    
    # Test default config
    config = RabbitMQConfig()
    assert config.host == 'localhost'
    assert config.port == 5672
    assert config.username == 'guest'
    
    # Test environment config
    os.environ['RABBITMQ_HOST'] = 'test-host'
    os.environ['RABBITMQ_PORT'] = '5673'
    config_env = RabbitMQConfig.from_env()
    assert config_env.host == 'test-host'
    assert config_env.port == 5673
    
    # Test connection URL
    url = config_env.get_connection_url()
    assert 'amqp://guest:guest@test-host:5673/' in url
    
    logger.info("✓ RabbitMQConfig tests passed")


def test_producer_instantiation():
    """Test producer instantiation"""
    logger.info("Testing FanoutProducer instantiation...")
    
    producer = FanoutProducer('test_exchange')
    assert producer.exchange_name == 'test_exchange'
    assert producer.connection is not None
    
    logger.info("✓ FanoutProducer instantiation test passed")


def test_consumer_instantiation():
    """Test consumer instantiation"""
    logger.info("Testing FanoutConsumer instantiation...")
    
    consumer = FanoutConsumer('test_exchange', 'test_queue')
    assert consumer.exchange_name == 'test_exchange'
    assert consumer.queue_name == 'test_queue'
    assert consumer.connection is not None
    
    # Test auto-generated queue name
    consumer2 = FanoutConsumer('test_exchange')
    assert consumer2.exchange_name == 'test_exchange'
    assert consumer2.queue_name == 'test_exchange_queue'
    
    logger.info("✓ FanoutConsumer instantiation test passed")


def main():
    """Run all tests"""
    logger.info("Starting messaging module tests...")
    
    try:
        test_config()
        test_producer_instantiation()
        test_consumer_instantiation()
        
        logger.info("🎉 All tests passed!")
        logger.info("The messaging module is ready to use.")
        logger.info("Note: To test actual message publishing/consuming, you'll need a running RabbitMQ server.")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    
    finally:
        # Clean up environment variables
        os.environ.pop('RABBITMQ_HOST', None)
        os.environ.pop('RABBITMQ_PORT', None)


if __name__ == "__main__":
    main()