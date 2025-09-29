"""Event publisher for the CMS system."""
import json
import logging
import uuid
from typing import Dict, Any
import requests

from src.cms.models.events import CMSEvent
from src.cms.events.connection import rabbitmq_connection
from config.settings import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes events to RabbitMQ and triggers n8n workflows."""
    
    def __init__(self):
        self.connection = rabbitmq_connection
    
    def publish_event(self, event: CMSEvent) -> bool:
        """
        Publish an event to RabbitMQ.
        
        Args:
            event: The event to publish
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            # Generate event ID if not provided
            if not event.event_id:
                event.event_id = str(uuid.uuid4())
            
            # Convert event to dictionary for JSON serialization
            event_data = event.dict()
            
            # Convert datetime to ISO format string for JSON serialization
            if 'timestamp' in event_data:
                if hasattr(event_data['timestamp'], 'isoformat'):
                    event_data['timestamp'] = event_data['timestamp'].isoformat()
            
            # Publish to RabbitMQ
            success = self.connection.publish_message(
                message=event_data,
                routing_key=event.routing_key or "default",
                exchange=event.exchange
            )
            
            if success:
                logger.info(f"Published event {event.event_id} of type {event.event_type}")
                
                # Trigger n8n workflow if needed
                self._trigger_n8n_workflow(event)
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def _trigger_n8n_workflow(self, event: CMSEvent):
        """
        Trigger n8n workflow via webhook.
        
        Args:
            event: The event that might trigger a workflow
        """
        try:
            # Only trigger n8n for specific event types
            workflow_triggers = [
                "user.created",
                "content.published",
                "workflow.triggered"
            ]
            
            if event.event_type in workflow_triggers:
                webhook_url = f"{settings.n8n_webhook_url}/cms-event"
                
                payload = {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data,
                    "metadata": event.metadata
                }
                
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully triggered n8n workflow for event {event.event_id}")
                else:
                    logger.warning(f"n8n webhook returned status {response.status_code}")
                    
        except requests.RequestException as e:
            logger.warning(f"Failed to trigger n8n workflow: {e}")
        except Exception as e:
            logger.error(f"Unexpected error triggering n8n workflow: {e}")
    
    def publish_user_event(self, user_id: str, action: str, additional_data: Dict[str, Any] = None) -> bool:
        """
        Publish a user-related event.
        
        Args:
            user_id: ID of the user
            action: Action performed (created, updated, deleted)
            additional_data: Additional event data
            
        Returns:
            bool: True if published successfully
        """
        from src.cms.models.events import UserEvent
        
        event = UserEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action
        )
        
        if additional_data:
            event.data.update(additional_data)
        
        return self.publish_event(event)
    
    def publish_content_event(self, content_id: str, action: str, content_type: str = "article", 
                            additional_data: Dict[str, Any] = None) -> bool:
        """
        Publish a content-related event.
        
        Args:
            content_id: ID of the content
            action: Action performed (created, updated, published, deleted)
            content_type: Type of content
            additional_data: Additional event data
            
        Returns:
            bool: True if published successfully
        """
        from src.cms.models.events import ContentEvent
        
        event = ContentEvent(
            event_id=str(uuid.uuid4()),
            content_id=content_id,
            action=action,
            content_type=content_type
        )
        
        if additional_data:
            event.data.update(additional_data)
        
        return self.publish_event(event)
    
    def publish_workflow_event(self, workflow_name: str, trigger_data: Dict[str, Any]) -> bool:
        """
        Publish a workflow trigger event.
        
        Args:
            workflow_name: Name of the workflow to trigger
            trigger_data: Data to pass to the workflow
            
        Returns:
            bool: True if published successfully
        """
        from src.cms.models.events import WorkflowEvent
        
        event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            workflow_name=workflow_name,
            trigger_data=trigger_data
        )
        
        return self.publish_event(event)


# Global publisher instance
event_publisher = EventPublisher()