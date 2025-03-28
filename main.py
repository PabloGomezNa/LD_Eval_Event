from metriclogic.metricsrelation import build_metrics_index
from consumer.rabbitmq_consumer import start_consumer

def main():
    #Build all metrics in memory event mapping
    all_metrics, event_map = build_metrics_index()
    
    print("In-memory event mapping for Metrics created.")
    
    
    #Here we should also add the call to the API to get the students names of all the projecst and create another file/in-memory mapping
    
    # Start the consumer with our event_map
    start_consumer(event_map)
    # The consumer blocks, waiting for messages.
    # (If you need concurrency or multiple threads, adjust accordingly.)

if __name__ == "__main__":
    main()




