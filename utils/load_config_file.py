import json, os

def load_sources_config()-> dict:
    '''
    Load the JSON configuration for event sources.
    '''
     # Determine config file path (env override or default)
    config_path = os.getenv("SOURCES_CONFIG", "sources_config.json")
    # Read and parse the JSON configuration
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)



def get_event_meta(event_type: str) -> dict | None:
    '''
    Retrieve metadata for a given event type from sources_config.
    '''       
    event_meta=load_sources_config().get(event_type)
    
    return event_meta
