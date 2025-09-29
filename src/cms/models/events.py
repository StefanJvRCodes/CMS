"""Event models for the CMS system."""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """Available event types in the CMS system."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_PUBLISHED = "content.published"
    CONTENT_DELETED = "content.deleted"
    SYSTEM_NOTIFICATION = "system.notification"
    WORKFLOW_TRIGGERED = "workflow.triggered"


class CMSEvent(BaseModel):
    """Base event model for all CMS events."""
    
    event_id: str = Field(..., description="Unique identifier for the event")
    event_type: EventType = Field(..., description="Type of the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the event occurred")
    source: str = Field(..., description="Source system or component that generated the event")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking related events")
    
    # Event payload
    data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Event routing
    routing_key: Optional[str] = Field(None, description="RabbitMQ routing key")
    exchange: str = Field("cms_events", description="RabbitMQ exchange name")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data


class UserEvent(CMSEvent):
    """User-related event."""
    
    def __init__(self, user_id: str, action: str, **kwargs):
        super().__init__(
            event_type=getattr(EventType, f"USER_{action.upper()}"),
            source="user_service",
            data={"user_id": user_id, "action": action},
            routing_key=f"user.{action.lower()}",
            **kwargs
        )


class ContentEvent(CMSEvent):
    """Content-related event."""
    
    def __init__(self, content_id: str, action: str, content_type: str = "article", **kwargs):
        super().__init__(
            event_type=getattr(EventType, f"CONTENT_{action.upper()}"),
            source="content_service",
            data={"content_id": content_id, "action": action, "content_type": content_type},
            routing_key=f"content.{action.lower()}",
            **kwargs
        )


class WorkflowEvent(CMSEvent):
    """Workflow-related event for n8n integration."""
    
    def __init__(self, workflow_name: str, trigger_data: Dict[str, Any], **kwargs):
        super().__init__(
            event_type=EventType.WORKFLOW_TRIGGERED,
            source="workflow_service",
            data={"workflow_name": workflow_name, "trigger_data": trigger_data},
            routing_key="workflow.triggered",
            **kwargs
        )