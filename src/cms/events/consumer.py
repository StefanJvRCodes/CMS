"""Event consumer for the CMS system."""
import json
import logging
from typing import Dict, Any, Callable
import pika

from src.cms.events.connection import rabbitmq_connection
from src.cms.models.events import CMSEvent, EventType
from config.settings import settings

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes events from RabbitMQ and processes them."""
    
    def __init__(self):
        self.connection = rabbitmq_connection
        self.event_handlers: Dict[str, Callable[[CMSEvent], None]] = {}
    
    def register_handler(self, event_type: EventType, handler: Callable[[CMSEvent], None]):
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: The event type to handle
            handler: The handler function
        """
        self.event_handlers[event_type.value] = handler
        logger.info(f"Registered handler for event type: {event_type.value}")
    
    def process_message(self, channel, method, properties, body):
        """
        Process a message received from RabbitMQ.
        
        Args:
            channel: The channel object
            method: The method frame
            properties: The properties
            body: The message body
        """
        try:
            # Parse the message
            message_data = json.loads(body.decode('utf-8'))
            event = CMSEvent(**message_data)
            
            logger.info(f"Processing event {event.event_id} of type {event.event_type}")
            
            # Find and execute the appropriate handler
            handler = self.event_handlers.get(event.event_type)
            if handler:
                handler(event)
                logger.info(f"Successfully processed event {event.event_id}")
            else:
                logger.warning(f"No handler found for event type: {event.event_type}")
                # Still acknowledge the message to avoid reprocessing
            
            # Acknowledge the message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
            # Reject the message and don't requeue
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject the message and requeue for retry
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self, queue: str = None):
        """
        Start consuming messages from the specified queue.
        
        Args:
            queue: Queue name to consume from (defaults to settings.default_queue)
        """
        queue = queue or settings.default_queue
        
        logger.info(f"Starting to consume messages from queue: {queue}")
        
        try:
            success = self.connection.consume_messages(queue, self.process_message)
            if not success:
                logger.error("Failed to start consuming messages")
        except KeyboardInterrupt:
            logger.info("Stopping message consumption...")
            self.connection.channel.stop_consuming()
        except Exception as e:
            logger.error(f"Error in message consumption: {e}")


class CMSEventHandlers:
    """Default event handlers for CMS events."""
    
    @staticmethod
    def handle_user_created(event: CMSEvent):
        """Handle user creation events."""
        user_id = event.data.get('user_id')
        logger.info(f"User created: {user_id}")
        
        # Example: Send welcome email, create user profile, etc.
        print(f"🎉 Welcome new user: {user_id}")
    
    @staticmethod
    def handle_user_updated(event: CMSEvent):
        """Handle user update events."""
        user_id = event.data.get('user_id')
        logger.info(f"User updated: {user_id}")
        
        # Example: Update search index, notify related services, etc.
        print(f"📝 User profile updated: {user_id}")
    
    @staticmethod
    def handle_user_deleted(event: CMSEvent):
        """Handle user deletion events."""
        user_id = event.data.get('user_id')
        logger.info(f"User deleted: {user_id}")
        
        # Example: Clean up user data, revoke access, etc.
        print(f"🗑️ User deleted: {user_id}")
    
    @staticmethod
    def handle_content_created(event: CMSEvent):
        """Handle content creation events."""
        content_id = event.data.get('content_id')
        content_type = event.data.get('content_type', 'unknown')
        logger.info(f"Content created: {content_id} ({content_type})")
        
        # Example: Index content, generate thumbnails, etc.
        print(f"📄 New content created: {content_id} ({content_type})")
    
    @staticmethod
    def handle_content_published(event: CMSEvent):
        """Handle content publication events."""
        content_id = event.data.get('content_id')
        content_type = event.data.get('content_type', 'unknown')
        logger.info(f"Content published: {content_id} ({content_type})")
        
        # Example: Notify subscribers, update sitemap, cache content, etc.
        print(f"🚀 Content published: {content_id} ({content_type})")
    
    @staticmethod
    def handle_workflow_triggered(event: CMSEvent):
        """Handle workflow trigger events."""
        workflow_name = event.data.get('workflow_name')
        logger.info(f"Workflow triggered: {workflow_name}")
        
        # Example: Log workflow execution, update metrics, etc.
        print(f"⚙️ Workflow triggered: {workflow_name}")


def setup_default_handlers(consumer: EventConsumer):
    """Set up default event handlers."""
    handlers = CMSEventHandlers()
    
    consumer.register_handler(EventType.USER_CREATED, handlers.handle_user_created)
    consumer.register_handler(EventType.USER_UPDATED, handlers.handle_user_updated)
    consumer.register_handler(EventType.USER_DELETED, handlers.handle_user_deleted)
    consumer.register_handler(EventType.CONTENT_CREATED, handlers.handle_content_created)
    consumer.register_handler(EventType.CONTENT_PUBLISHED, handlers.handle_content_published)
    consumer.register_handler(EventType.WORKFLOW_TRIGGERED, handlers.handle_workflow_triggered)
    
    logger.info("Default event handlers set up successfully")


# Global consumer instance
event_consumer = EventConsumer()
setup_default_handlers(event_consumer)