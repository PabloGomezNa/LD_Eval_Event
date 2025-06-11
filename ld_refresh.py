import os, logging, requests
import time
from API_calls.StudentDatafromLDRESTAPI import build_team_students_map
from config.quality_model_config    import load_qualitymodel_map, choose_qualitymodel
from config.load_config_file        import get_event_meta, get_available_events
from database.mongo_client         import db        

API_URL       = os.getenv("EVAL_API_URL", "http://localhost:5001/api/event")
TEAM_STUDENTS = build_team_students_map()
QM_MAP        = load_qualitymodel_map()

EVENT_TYPES   = ["push", "task", "userstory"]



def team_is_active(team_id: str) -> bool:
    """Function to check if a team has any activity in the database.
    If not active, it will not trigger any events."""
    coll = f"metrics.{team_id}" # We will only check the metrics collection, because if it has metrics, the factors and indicators collections will also have data.
    return coll in db.list_collection_names() and db[coll].estimated_document_count() > 0



def trigger_team_event(team_id: str, event_type: str) -> None:
    '''Function to trigger an event for a team.
    It will send a POST request to the API with the event data.'''
    payload = {
        "event_type"  : event_type,
        "prj"         : team_id,
        "author_login": "system",
        "quality_model": choose_qualitymodel(team_id, None, QM_MAP)
    }
    start = time.perf_counter()
    r = requests.post(API_URL, json=payload, timeout=(0.2, 1)) #connect timeout 0.2s, read timeout 1s
    logging.info("POST tardó %.3f s", time.perf_counter() - start)

    logging.info("team=%s event=%s → status=%s", team_id, event_type, r.status_code)


def run_daily_refresh() -> None:
    '''Function to run the daily refresh of events.'''
    for team in TEAM_STUDENTS.keys(): # Get all the teams from the TEAM_STUDENTS map
        if not team_is_active(team):
            logging.info("Equipo %s sin actividad previa; se omite.", team) # If the team is not active, skip it
            continue
        
        events= get_available_events()
        for event in events: # If the team is active, trigger all the events
            trigger_team_event(team, event)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
    run_daily_refresh()
    
