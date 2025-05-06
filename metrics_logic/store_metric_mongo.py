from pymongo import MongoClient
from datetime import datetime
from zoneinfo import ZoneInfo
import os


#def store_metric_result(team_name: str, metric_name: str, scope: str, final_val: float, event_type: str, student_name: str = None, aggregator_doc: dict = None):
def store_metric_result(team_name: str, metric_def: str, final_val: float, event_type: str, student_name: str = None, aggregator_doc: dict = None):
    '''
    Insert a metric result into the MongoDB database.
    '''
    # Sets the collection name to the team name + "_metrics"     
    collection_name = f"{team_name}_metrics"
    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]
    # Sets the evaluation date to the current date and time in the Europe/Madrid timezone
    evaluation_date = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d,%H:%M:%S")
    
    # Metric label, its the name .properties file, for instance task_effort.properties metric, the name is task_effort
    full_path = metric_def["filePath"]
    filename = os.path.basename(full_path)
    metric_label = os.path.splitext(filename)[0]

    # Unique _id = project‑metric‑[student‑]date
    id_parts = [team_name, metric_label, evaluation_date]
    if student_name:
        id_parts.insert(2, student_name)           # add between team & date
    doc_id = "-".join(id_parts)

    # Compose the info block, with parameters and formula
    info_lines = [
        f"parameters: {{evaluationDate={evaluation_date}}}",
        f"query-properties: {metric_def['params']}",
    ]
    if aggregator_doc:
        info_lines.append(f"executionResults: {aggregator_doc}")
    info_lines.append(f"formula: {metric_def['formula']}")
    info_lines.append(f"value: {final_val}")
    info = "\n".join(info_lines)

    # Final Mongo document to be inserted
    doc = {
        "_id":           doc_id,
        "description":   metric_def.get("description", ""),
        "evaluationDate": evaluation_date,
        "info":          info,
        "metric":        metric_label,
        "name":          metric_def["name"],
        "project":       team_name,
        "source":        f"mongodb:27017/mongo.{collection_name}",
        "type":          "metrics",
        "value":         final_val,
        "weights":       metric_def.get("weights", []),
        "scope":         "individual" if student_name else "team",
        "event_type":    event_type,
    }
    if student_name:    # If the metric is for a student, add the student name to the document
        doc["student_name"] = student_name
        
    # Insert into MongoDB
    db[collection_name].insert_one(doc)