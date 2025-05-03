from pymongo import MongoClient
from datetime import datetime
import os


def store_indicator_result(team_name:str, indicator_def, final_value: float, intermediate_factor_values):
    
    collection_name = f"{team_name}_factors"

    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]

    evaluation_date = datetime.utcnow().strftime("%Y-%m-%d,%H:%M:%S")

    # Metric label, its the name .properties file, for instance task_effort.properties metric, the name is task_effort

    full_path = indicator_def["filePath"]
    filename = os.path.basename(full_path)
    indicator_label = os.path.splitext(filename)[0]
    
    
    _id_parts = [team_name, indicator_def['name'], evaluation_date]

    '''
    #the info field is:
    
    "metrics": { metric_name: (value: , weight:); ...} formula: {formula} value: {value}",
    '''
    factor_info= ""
    for factor_name, factor_value in intermediate_factor_values.items():
        factor_info +=f"{factor_name} (value: {factor_value[0][1]}, {indicator_def['weights']}); "
    
    info_lines = f"factors:{ {factor_info} }, formula: {indicator_def['formula']}, value: {final_value}"
    
    doc = {
        "_id"          : "-".join(_id_parts),
        "name"         : indicator_def['name'],
        "description"  : indicator_def['description'],
        "project"      : team_name,
        "evaluationDate": evaluation_date,
        "indicator"       : indicator_label,
        "info"         : info_lines, 
        "value"        : final_value,
    }

    db[collection_name].insert_one(doc)


