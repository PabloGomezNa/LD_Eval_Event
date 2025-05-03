from pymongo import MongoClient
from datetime import datetime
import os


def store_factor_result(team_name:str, factor_def, final_value: float, intermediate_metric_values):
    
    collection_name = f"{team_name}_factors"

    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]

    evaluation_date = datetime.utcnow().strftime("%Y-%m-%d,%H:%M:%S")

    # Metric label, its the name .properties file, for instance task_effort.properties metric, the name is task_effort

    full_path = factor_def["filePath"]
    filename = os.path.basename(full_path)
    factor_label = os.path.splitext(filename)[0]
    
    
    _id_parts = [team_name, factor_def['name'], evaluation_date]

    '''
    #the info field is:
    
    "metrics": { metric_name: (value: , weight:); ...} formula: {formula} value: {value}",
    '''
    metric_info= ""
    for metric_name, metric_value in intermediate_metric_values.items():
        metric_info +=f"{metric_name} (value: {metric_value[0][1]}, {factor_def['weights']}); "
    
    info_lines = f"metrics:{ {metric_info} }, formula: {factor_def['formula']}, value: {final_value}"
    
    doc = {
        "_id"          : "-".join(_id_parts),
        "name"         : factor_def['name'],
        "description"  : factor_def['description'],
        "project"      : team_name,
        "evaluationDate": evaluation_date,
        "factor"       : factor_label,
        "info"         : info_lines, 
        "value"        : final_value,
    }

    db[collection_name].insert_one(doc)


