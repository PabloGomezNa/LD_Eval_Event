from pymongo import MongoClient
from datetime import datetime
from zoneinfo import ZoneInfo
import os


def store_indicator_result(team_name:str, indicator_def: dict, final_value: float, intermediate_factor_values: dict)-> None:
    '''
    Insert a indicator result into the MongoDB database under a certain collection name.
    '''
    # Sets the collection name to the team name + "_indicators"    
    collection_name = f"{team_name}_indicators"
    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]

    # Sets the evaluation date to the current date and time in the Europe/Madrid timezone
    evaluation_date = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d,%H:%M:%S")

    # Indicator label, its the name .properties file, for instance task_effort.properties metric, the name is task_effort
    full_path = indicator_def["filePath"]
    filename = os.path.basename(full_path)
    factor_label = os.path.splitext(filename)[0]
    
    # Build a unique _id: team-factorName-timestamp
    _id_parts = [team_name, indicator_def['name'], evaluation_date]

    # Compose info string: list each (student or metric, value, weights)
    factor_info_parts = []
    for factor_name, tuples in intermediate_factor_values.items():
        for student, val in tuples:
            # if student name is None, we use the mretrics name
            label = student if student is not None else factor_name
            factor_info_parts.append(
                f"('{label}', value: {val}, weights: {indicator_def.get('weights', [])})"
            )
    metric_info = "; ".join(factor_info_parts)
    
    info_lines = f"indicators:{ {metric_info} }, formula: {indicator_def['formula']}, value: {final_value}"
    
    # Final Mongo document to be inserted
    doc = {
        "_id"          : "-".join(_id_parts),
        "name"         : indicator_def['name'],
        "description"  : indicator_def['description'],
        "project"      : team_name,
        "evaluationDate": evaluation_date,
        "indicator"       : factor_label,
        "info"         : info_lines, 
        "value"        : final_value,
    }

     # Insert into MongoDB
    db[collection_name].insert_one(doc)
