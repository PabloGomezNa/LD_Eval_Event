from consumer.rabbitmq_consumer import start_consumer
from metriclogic.metricsrelation import build_metrics_index

from LearningDashboardAPIREST_Call.StudentDatafromLDRESTAPI import fetch_team_students_map

        
def main():
    
    #Build all metrics in memory event mapping
    all_metrics, event_map = build_metrics_index()
    print("In-memory event mapping for Metrics created.")
    
    #print this mapping to see if it is correct. This will be commented in the future
    for event, metrics in event_map.items():
        print(f"Event: {event}")
        for metric in metrics:
            print(f"  Metric: {metric['name']} (scope={metric['scope']})")
    
    #Here we should also add the call to the API to get the students names of all the projecst and create another file/in-memory mapping
    team_students_map = fetch_team_students_map()
    print(team_students_map) #Print the mapping to see
    
    # Start the consumer with our event_map
    start_consumer(event_map, team_students_map) #This consumer will listen all the events, once he receives one, 
    #it will call the function on_message with the event_map and team_students_map as parameters.
    #This on message function withg the data received from the event, will handle all the logic of the metric recalculation.
    

if __name__ == "__main__":
    main()




