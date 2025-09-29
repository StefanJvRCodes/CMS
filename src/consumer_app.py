"""Standalone event consumer application."""
import logging
import signal
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cms.events.consumer import event_consumer
from config.settings import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal. Stopping consumer...")
    sys.exit(0)


def main():
    """Main function to run the event consumer."""
    logger.info("Starting CMS Event Consumer...")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start consuming events
        event_consumer.start_consuming(settings.default_queue)
    except Exception as e:
        logger.error(f"Error in event consumer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()