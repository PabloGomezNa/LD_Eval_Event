import json, os

def load_sources_config():
    config_path = os.getenv("SOURCES_CONFIG", "sources_config.json")
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)



def get_event_meta(event_type: str) -> dict | None:
    """Return {'identity_key': 'GITHUB', 'collection_suffix': 'commits'} or None."""
       
    event_meta=load_sources_config().get(event_type)
    
    return event_meta
