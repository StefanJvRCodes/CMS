# CMS Core Messaging Module

This module provides RabbitMQ messaging functionality with fanout queues for the CMS (Central Management System).

## Features

- **Fanout Exchange Support**: Publishes messages to all bound queues
- **Automatic Connection Management**: Handles connection lifecycle and reconnection
- **Environment-based Configuration**: Configure via environment variables
- **JSON Message Serialization**: Automatic serialization/deserialization
- **Error Handling & Logging**: Comprehensive error handling with logging
- **Context Manager Support**: Clean resource management

## Components

### 1. RabbitMQConfig
Configuration management for RabbitMQ connections.

```python
from core.messaging import RabbitMQConfig

# Use default configuration (from environment)
config = RabbitMQConfig.from_env()

# Or create custom configuration
config = RabbitMQConfig(
    host='localhost',
    port=5672,
    username='guest',
    password='guest'
)
```

### 2. FanoutProducer
Publishes messages to fanout exchanges.

```python
from core.messaging import FanoutProducer

# Using context manager (recommended)
with FanoutProducer('my_exchange') as producer:
    producer.publish_message({'type': 'notification', 'data': 'Hello World'})
    producer.publish_text('Simple text message')

# Manual management
producer = FanoutProducer('my_exchange')
producer.setup_exchange()
producer.publish_message({'user_id': 123, 'action': 'login'})
producer.close()
```

### 3. FanoutConsumer
Consumes messages from fanout exchanges.

```python
from core.messaging import FanoutConsumer

def handle_message(message_info):
    data = message_info['data']
    print(f"Received: {data}")

# Consume messages
consumer = FanoutConsumer('my_exchange', 'my_queue')
consumer.consume_messages(handle_message)
```

## Environment Variables

Create a `.env` file or set these environment variables:

```bash
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
RABBITMQ_CONNECTION_TIMEOUT=30
RABBITMQ_HEARTBEAT=600
```

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Examples

See the `examples/` directory for complete usage examples:

- `producer_example.py`: Demonstrates message publishing
- `consumer_example.py`: Demonstrates message consumption

Run the examples:

```bash
# Terminal 1 - Start consumer
python examples/consumer_example.py

# Terminal 2 - Send messages
python examples/producer_example.py
```

## Message Format

Messages are automatically serialized to JSON. The consumer receives messages in this format:

```python
{
    'data': <original_message_data>,
    'exchange': 'exchange_name',
    'routing_key': '',
    'delivery_tag': 1,
    'properties': {
        'content_type': 'application/json',
        'timestamp': <timestamp>,
        'message_id': <message_id>
    }
}
```

## Error Handling

The module includes comprehensive error handling:

- Connection failures with automatic retry
- Message serialization errors
- Consumer processing errors with message requeue
- Proper resource cleanup

## Logging

All components use Python's standard logging module. Configure logging in your application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```