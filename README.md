# CMS
Central Management System - Just a way for me to organise stuff

## RabbitMQ Messaging Module

The CMS now includes a core messaging module that provides RabbitMQ fanout queue functionality.

### Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure RabbitMQ (copy `.env.example` to `.env` and modify as needed):
```bash
cp .env.example .env
```

3. Use the messaging system:
```python
from core.messaging import FanoutProducer, FanoutConsumer

# Send messages
with FanoutProducer('my_exchange') as producer:
    producer.publish_message({'type': 'notification', 'data': 'Hello World'})

# Receive messages
def handle_message(message_info):
    print(f"Received: {message_info['data']}")

consumer = FanoutConsumer('my_exchange', 'my_queue')
consumer.consume_messages(handle_message)
```

### Examples

See the `examples/` directory for complete usage examples:
- `examples/producer_example.py` - Message publishing example
- `examples/consumer_example.py` - Message consumption example

### Testing

Run the basic functionality test:
```bash
python test_messaging.py
```

For detailed documentation, see `core/messaging/README.md`.
