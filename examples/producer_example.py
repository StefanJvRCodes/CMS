#!/usr/bin/env python3
"""
Example RabbitMQ Fanout Producer
Demonstrates how to publish messages to a fanout exchange
"""
import sys
import os
import logging
import time
from datetime import datetime

# Add the parent directory to the path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.messaging import FanoutProducer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main producer example"""
    exchange_name = "cms_notifications"
    
    try:
        # Create producer
        with FanoutProducer(exchange_name) as producer:
            logger.info(f"Producer connected to exchange '{exchange_name}'")
            
            # Send some sample messages
            messages = [
                {"type": "user_created", "user_id": 123, "username": "johndoe"},
                {"type": "order_placed", "order_id": 456, "amount": 99.99},
                {"type": "system_alert", "level": "info", "message": "System health check passed"},
                "Simple text message",
                {"type": "data_update", "table": "users", "records_affected": 15}
            ]
            
            for i, message in enumerate(messages, 1):
                success = producer.publish_message(message)
                if success:
                    logger.info(f"Message {i} published successfully")
                else:
                    logger.error(f"Failed to publish message {i}")
                
                # Small delay between messages
                time.sleep(1)
            
            # Send a final message with current timestamp
            final_message = {
                "type": "producer_finished",
                "timestamp": datetime.now().isoformat(),
                "total_messages": len(messages) + 1
            }
            producer.publish_message(final_message)
            logger.info("Final message sent, producer finished")
            
    except Exception as e:
        logger.error(f"Producer error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()