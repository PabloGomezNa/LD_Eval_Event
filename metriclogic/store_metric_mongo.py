from pymongo import MongoClient
from datetime import datetime



def store_metric_result(team_name: str, metric_name: str, scope: str, final_val: float, event_type: str, student_name: str = None, aggregator_doc: dict = None):
    """
    Inserts a document representing the computed metric result into
    the MongoDB '{team_name}_metrics' collection.
    """
    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]

    collection_name = f"{team_name}_metrics"
    doc = {
        "team_name": team_name,
        "metric_name": metric_name,
        "scope": scope,               # "individual" or "team"
        "value": final_val,           # numeric result
        "event_type": event_type,
        "computed_at": datetime.utcnow(),
    }

    # If scope is 'individual', store student name:
    if scope == "individual" and student_name:
        doc["student_name"] = student_name

    # Raw aggregator results and partial aggregator data in the same record:
    if aggregator_doc:
        doc["aggregator_results"] = aggregator_doc

    db[collection_name].insert_one(doc)