# CMS - Event-Driven Central Management System

A Python-based Content Management System built with an event-driven architecture using RabbitMQ and n8n for workflow automation.

## 🏗️ Architecture

This CMS implements an event-driven architecture with the following components:

- **FastAPI** - REST API for content and user management
- **RabbitMQ** - Message broker for event publishing/consuming
- **n8n** - Workflow automation platform
- **Python** - Core application logic and event handlers

## 🚀 Features

- **Event-Driven Architecture**: All operations publish events to RabbitMQ
- **REST API**: Full CRUD operations for users and content
- **Workflow Integration**: Automatic n8n workflow triggers
- **Scalable Design**: Microservices-ready with Docker support
- **Real-time Processing**: Asynchronous event processing

## 📁 Project Structure

```
CMS/
├── src/
│   ├── cms/
│   │   ├── api/           # REST API routes
│   │   ├── events/        # Event system (publisher, consumer, connection)
│   │   └── models/        # Data models and event schemas
│   ├── main.py           # FastAPI application
│   └── consumer_app.py   # Standalone event consumer
├── config/
│   └── settings.py       # Configuration management
├── n8n/
│   └── workflows/        # Example n8n workflow configurations
├── scripts/
│   └── test_events.py    # Event testing utility
├── docker-compose.yml    # Infrastructure setup
├── Dockerfile           # Application container
└── requirements.txt     # Python dependencies
```

## 🛠️ Setup & Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CMS
   ```

2. **Start the infrastructure**
   ```bash
   docker-compose up -d rabbitmq n8n
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Start the API server**
   ```bash
   python src/main.py
   ```

6. **Start the event consumer** (in another terminal)
   ```bash
   python src/consumer_app.py
   ```

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 🌐 Service URLs

- **CMS API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (cms_user/cms_password)
- **n8n Workflow Platform**: http://localhost:5678 (admin/admin123)

## 📊 API Endpoints

### Users
- `POST /api/v1/users` - Create a new user
- `PUT /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

### Content
- `POST /api/v1/content` - Create new content
- `PUT /api/v1/content/{content_id}/publish` - Publish content

### Workflows
- `POST /api/v1/workflows/trigger` - Trigger an n8n workflow

### System
- `GET /api/v1/health` - Health check
- `GET /info` - System information

## 🎯 Event Types

The system publishes the following event types:

- `user.created` - New user registration
- `user.updated` - User profile changes
- `user.deleted` - User removal
- `content.created` - New content creation
- `content.updated` - Content modifications
- `content.published` - Content publication
- `content.deleted` - Content removal
- `workflow.triggered` - n8n workflow activation

## 🔧 Testing

### Test Event Publishing

```bash
python scripts/test_events.py
```

### API Testing

Use the interactive API documentation at http://localhost:8000/docs to test endpoints.

### Example API Calls

```bash
# Create a user
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "role": "editor"}'

# Create content
curl -X POST "http://localhost:8000/api/v1/content" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Article", "content": "Article content here", "author_id": "user_123"}'

# Trigger workflow
curl -X POST "http://localhost:8000/api/v1/workflows/trigger" \
  -H "Content-Type: application/json" \
  -d '{"workflow_name": "send_email", "trigger_data": {"recipient": "admin@example.com"}}'
```

## ⚙️ Configuration

Configuration is managed through environment variables. See `.env.example` for available options:

- `RABBITMQ_URL` - RabbitMQ connection string
- `N8N_WEBHOOK_URL` - n8n webhook endpoint
- `DEBUG` - Enable debug mode
- `DEFAULT_EXCHANGE` - Default RabbitMQ exchange name
- `DEFAULT_QUEUE` - Default RabbitMQ queue name

## 🔄 Workflow Integration

The CMS automatically triggers n8n workflows for specific events:

1. **user.created** - Welcome email, user onboarding
2. **content.published** - Notifications, social media posting
3. **workflow.triggered** - Custom workflow execution

Import the example workflow from `n8n/workflows/cms-example-workflow.json` into your n8n instance.

## 🚀 Production Deployment

For production deployment:

1. Set up proper environment variables
2. Use a production WSGI server (Gunicorn recommended)
3. Set up SSL/TLS certificates
4. Configure proper RabbitMQ credentials
5. Set up monitoring and logging
6. Use a reverse proxy (Nginx recommended)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.
