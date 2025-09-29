#!/usr/bin/env python3
"""Test script to publish sample events to the CMS system."""
import sys
import os
import time

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cms.events.publisher import event_publisher


def test_user_events():
    """Test user-related events."""
    print("🧪 Testing user events...")
    
    # Test user creation
    success = event_publisher.publish_user_event(
        user_id="user_123",
        action="created",
        additional_data={
            "name": "John Doe",
            "email": "john@example.com",
            "role": "editor"
        }
    )
    print(f"User created event: {'✅' if success else '❌'}")
    time.sleep(1)
    
    # Test user update
    success = event_publisher.publish_user_event(
        user_id="user_123",
        action="updated",
        additional_data={
            "name": "John Smith",
            "role": "admin"
        }
    )
    print(f"User updated event: {'✅' if success else '❌'}")
    time.sleep(1)


def test_content_events():
    """Test content-related events."""
    print("📄 Testing content events...")
    
    # Test content creation
    success = event_publisher.publish_content_event(
        content_id="article_456",
        action="created",
        content_type="article",
        additional_data={
            "title": "Getting Started with Event-Driven Architecture",
            "author_id": "user_123",
            "status": "draft"
        }
    )
    print(f"Content created event: {'✅' if success else '❌'}")
    time.sleep(1)
    
    # Test content publication
    success = event_publisher.publish_content_event(
        content_id="article_456",
        action="published",
        content_type="article",
        additional_data={
            "published_at": "2024-01-01T12:00:00Z"
        }
    )
    print(f"Content published event: {'✅' if success else '❌'}")
    time.sleep(1)


def test_workflow_events():
    """Test workflow-related events."""
    print("⚙️ Testing workflow events...")
    
    # Test workflow trigger
    success = event_publisher.publish_workflow_event(
        workflow_name="send_notification",
        trigger_data={
            "recipient": "admin@example.com",
            "message": "New content has been published",
            "priority": "normal"
        }
    )
    print(f"Workflow triggered event: {'✅' if success else '❌'}")
    time.sleep(1)


def main():
    """Run all event tests."""
    print("🚀 Starting CMS Event Tests")
    print("=" * 50)
    
    try:
        test_user_events()
        print()
        
        test_content_events()
        print()
        
        test_workflow_events()
        print()
        
        print("✅ All event tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()