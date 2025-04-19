from pymongo import MongoClient
from datetime import datetime



#def store_metric_result(team_name: str, metric_name: str, scope: str, final_val: float, event_type: str, student_name: str = None, aggregator_doc: dict = None):
def store_metric_result(team_name: str, metric_def: str, final_val: float, event_type: str, student_name: str = None, aggregator_doc: dict = None):

    collection_name = f"{team_name}_metrics"

    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]

    evaluation_date = datetime.utcnow().strftime("%Y-%m-%d,%H:%M:%S")

    # Canonical metric label (e.g. modifiedlines_Patricia_Ortega_Gr)
    metric_label = metric_def["name"]

    # Unique _id = project‑metric‑[student‑]date
    id_parts = [team_name, metric_label, evaluation_date]
    if student_name:
        id_parts.insert(2, student_name)           # add between team & date
    doc_id = "-".join(id_parts)

    # Info block (same format the original Learning‑Dashboard uses)
    info_lines = [
        f"parameters: {{evaluationDate={evaluation_date}}}",
        f"query-properties: {metric_def['params']}",
    ]
    if aggregator_doc:
        info_lines.append(f"executionResults: {aggregator_doc}")
    info_lines.append(f"formula: {metric_def['formula']}")
    info_lines.append(f"value: {final_val}")
    info = "\n".join(info_lines)

    # Final Mongo document
    doc = {
        "_id":           doc_id,
        "description":   metric_def.get("description", ""),
        "evaluationDate": evaluation_date,
        "factors":       metric_def.get("factors", []),
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
    if student_name:
        doc["student_name"] = student_name

    db[collection_name].insert_one(doc)