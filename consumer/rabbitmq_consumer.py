import os
import json
import pika


from metriclogic.metric_recalculation import compute_metric_for_student, compute_metric_for_team



RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "ld_exchange")
RABBITMQ_EXCHANGE_TYPE = os.getenv("RABBITMQ_EXCHANGE_TYPE", "fanout")

def on_message(ch, method, properties, body,event_map, team_students_map):
    """
    Callback invoked whenever a new message arrives.
    """
    #Extract the body
    data = json.loads(body)
    print(data)
    #From the body extract the event_type and teamname
    event_type = data.get("event_type")
    team_name = data.get("team_name", {})
    print(f"Received event: {event_type}, team_name={team_name}")
    
    if not team_name:
        # If no team found in payload, skip
        print("No 'team' in payload, ignoring.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    
    
    # Retrieve the students for the team
    students = team_students_map.get(team_name, [])
    print("Students in team:", students)
    
    # Retieve the metric that will be recalculated
    triggered_metrics = event_map.get(event_type, [])
    
    print("Triggered metrics:", triggered_metrics)
    
    
    # Loop over the metrics that will be recalculated
    for metric_def in triggered_metrics:
        scope = metric_def.get("scope") # Get the scope of the metric, it can be "team" or "individual"
        if scope == "individual":#If the scope is "individual" 
            for student_name in students: #We loop over the students of the team and compute the metric for each one of them
                compute_metric_for_student(metric_def, student_name, team_name)
        else: #The scope is "team"
            compute_metric_for_team(metric_def, team_name) #We compute the metric of the team

    # Lastly acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)



def start_consumer(event_map, team_students_map):
    
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
    
    #?????????????????????????????????????????? THIS
    # We define a callback that includes event_map + team_students_map
    def callback(ch, method, props, body):
        on_message(ch, method, props, body, event_map, team_students_map)

    # Consume
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print("LD_Eval waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


