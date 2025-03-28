import os
import json
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "ld_exchange")
RABBITMQ_EXCHANGE_TYPE = os.getenv("RABBITMQ_EXCHANGE_TYPE", "fanout")

def on_message(ch, method, properties, body,event_map):
    """
    Callback invoked whenever a new message arrives.
    """
    data = json.loads(body)
    event_type = data.get("event_type")
    payload = data.get("payload", {})

    print(f"Received event: {event_type}, payload={payload}")
    
    #Metric recalculation
    triggered_metrics = event_map.get(event_type, [])
    
    for metric_def in triggered_metrics:
        print(f"Recompute metric '{metric_def['name']}' [scope={metric_def['scope']}]")

    # 2. Acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer(event_map):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection_params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Declare exchange
    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE,
                             exchange_type=RABBITMQ_EXCHANGE_TYPE,
                             durable=True)

    # Create a queue, bind to exchange
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=queue_name)

    # Consume
    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    print("LD_Eval waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


