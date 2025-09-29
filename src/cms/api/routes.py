"""API routes for the CMS system."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid

from src.cms.events.publisher import event_publisher
from src.cms.models.events import EventType

router = APIRouter()


# Request/Response Models
class UserCreateRequest(BaseModel):
    name: str
    email: str
    role: str = "user"


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class ContentCreateRequest(BaseModel):
    title: str
    content: str
    content_type: str = "article"
    author_id: str


class ContentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None


class WorkflowTriggerRequest(BaseModel):
    workflow_name: str
    trigger_data: Dict[str, Any]


class EventResponse(BaseModel):
    event_id: str
    message: str
    success: bool


# User Management Endpoints
@router.post("/users", response_model=EventResponse)
async def create_user(request: UserCreateRequest, background_tasks: BackgroundTasks):
    """Create a new user and publish a user creation event."""
    user_id = str(uuid.uuid4())
    
    # Simulate user creation logic here
    user_data = {
        "name": request.name,
        "email": request.email,
        "role": request.role,
        "created_at": "2024-01-01T00:00:00Z"  # In real app, use current timestamp
    }
    
    # Publish event in background
    def publish_event():
        success = event_publisher.publish_user_event(
            user_id=user_id,
            action="created",
            additional_data=user_data
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to publish user creation event")
    
    background_tasks.add_task(publish_event)
    
    return EventResponse(
        event_id=str(uuid.uuid4()),
        message=f"User {user_id} created successfully",
        success=True
    )


@router.put("/users/{user_id}", response_model=EventResponse)
async def update_user(user_id: str, request: UserUpdateRequest, background_tasks: BackgroundTasks):
    """Update a user and publish a user update event."""
    
    # Simulate user update logic here
    updated_data = {k: v for k, v in request.dict().items() if v is not None}
    updated_data["updated_at"] = "2024-01-01T00:00:00Z"
    
    # Publish event in background
    def publish_event():
        success = event_publisher.publish_user_event(
            user_id=user_id,
            action="updated",
            additional_data=updated_data
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to publish user update event")
    
    background_tasks.add_task(publish_event)
    
    return EventResponse(
        event_id=str(uuid.uuid4()),
        message=f"User {user_id} updated successfully",
        success=True
    )


@router.delete("/users/{user_id}", response_model=EventResponse)
async def delete_user(user_id: str, background_tasks: BackgroundTasks):
    """Delete a user and publish a user deletion event."""
    
    # Simulate user deletion logic here
    
    # Publish event in background
    def publish_event():
        success = event_publisher.publish_user_event(
            user_id=user_id,
            action="deleted"
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to publish user deletion event")
    
    background_tasks.add_task(publish_event)
    
    return EventResponse(
        event_id=str(uuid.uuid4()),
        message=f"User {user_id} deleted successfully",
        success=True
    )


# Content Management Endpoints
@router.post("/content", response_model=EventResponse)
async def create_content(request: ContentCreateRequest, background_tasks: BackgroundTasks):
    """Create new content and publish a content creation event."""
    content_id = str(uuid.uuid4())
    
    # Simulate content creation logic here
    content_data = {
        "title": request.title,
        "content": request.content,
        "author_id": request.author_id,
        "status": "draft",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    # Publish event in background
    def publish_event():
        success = event_publisher.publish_content_event(
            content_id=content_id,
            action="created",
            content_type=request.content_type,
            additional_data=content_data
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to publish content creation event")
    
    background_tasks.add_task(publish_event)
    
    return EventResponse(
        event_id=str(uuid.uuid4()),
        message=f"Content {content_id} created successfully",
        success=True
    )


@router.put("/content/{content_id}/publish", response_model=EventResponse)
async def publish_content(content_id: str, background_tasks: BackgroundTasks):
    """Publish content and trigger publication event."""
    
    # Simulate content publication logic here
    
    # Publish event in background
    def publish_event():
        success = event_publisher.publish_content_event(
            content_id=content_id,
            action="published",
            additional_data={"published_at": "2024-01-01T00:00:00Z"}
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to publish content publication event")
    
    background_tasks.add_task(publish_event)
    
    return EventResponse(
        event_id=str(uuid.uuid4()),
        message=f"Content {content_id} published successfully",
        success=True
    )


# Workflow Management Endpoints
@router.post("/workflows/trigger", response_model=EventResponse)
async def trigger_workflow(request: WorkflowTriggerRequest, background_tasks: BackgroundTasks):
    """Trigger an n8n workflow."""
    
    # Publish workflow event in background
    def publish_event():
        success = event_publisher.publish_workflow_event(
            workflow_name=request.workflow_name,
            trigger_data=request.trigger_data
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to trigger workflow")
    
    background_tasks.add_task(publish_event)
    
    return EventResponse(
        event_id=str(uuid.uuid4()),
        message=f"Workflow {request.workflow_name} triggered successfully",
        success=True
    )


# Health Check Endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CMS Event-Driven System"}