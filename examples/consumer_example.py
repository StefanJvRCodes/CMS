#!/usr/bin/env python3
"""
Example RabbitMQ Fanout Consumer
Demonstrates how to consume messages from a fanout exchange
"""
import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.messaging import FanoutConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def message_handler(message_info):
    """
    Handle received messages
    
    Args:
        message_info: Dictionary containing message data and metadata
    """
    try:
        data = message_info['data']
        exchange = message_info['exchange']
        
        logger.info(f"Received message from exchange '{exchange}':")
        
        # Handle different message types
        if isinstance(data, dict):
            message_type = data.get('type', 'unknown')
            logger.info(f"  Type: {message_type}")
            
            # Process specific message types
            if message_type == 'user_created':
                logger.info(f"  New user: {data.get('username')} (ID: {data.get('user_id')})")
            elif message_type == 'order_placed':
                logger.info(f"  Order ID: {data.get('order_id')}, Amount: ${data.get('amount')}")
            elif message_type == 'system_alert':
                logger.info(f"  Alert Level: {data.get('level')}, Message: {data.get('message')}")
            elif message_type == 'data_update':
                logger.info(f"  Table: {data.get('table')}, Records: {data.get('records_affected')}")
            elif message_type == 'producer_finished':
                logger.info(f"  Producer finished at: {data.get('timestamp')}")
                logger.info(f"  Total messages sent: {data.get('total_messages')}")
            else:
                logger.info(f"  Data: {data}")
        else:
            logger.info(f"  Text message: {data}")
        
        # Add processing timestamp
        logger.info(f"  Processed at: {datetime.now().isoformat()}")
        logger.info("-" * 50)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        logger.error(f"Message data: {message_info}")


def main():
    """Main consumer example"""
    exchange_name = "cms_notifications"
    queue_name = "cms_consumer_example"  # Use specific queue name for this example
    
    try:
        # Create consumer
        consumer = FanoutConsumer(exchange_name, queue_name)
        
        logger.info(f"Consumer starting for exchange '{exchange_name}' with queue '{queue_name}'")
        logger.info("Press Ctrl+C to stop consuming")
        
        # Start consuming messages (this will block)
        consumer.consume_messages(message_handler, auto_ack=False)
        
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.error(f"Consumer error: {e}")
        sys.exit(1)
    finally:
        try:
            consumer.close()
        except:
            pass


if __name__ == "__main__":
    main()