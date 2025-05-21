from datetime import datetime
from zoneinfo import ZoneInfo
import os

from database.mongo_client import get_collection


def store_factor_result(team_name:str, factor_def: dict, final_value: float, intermediate_metric_values: dict)-> None:
    '''
    Insert a indicator result into the MongoDB database under a certain collection name.
    '''
    # Sets the collection name to the team name + "_indicators"   
    collection = get_collection(f"factors.{team_name}")

    # Sets the evaluation date to the current date and time in the Europe/Madrid timezone
   #evaluation_date = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d,%H:%M:%S")
    evaluation_date = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")

    # Factor label, its the name .properties file, for instance task_effort.properties metric, the name is task_effort
    full_path = factor_def["filePath"]
    filename = os.path.basename(full_path)
    factor_label = os.path.splitext(filename)[0]
    
    # Build a unique _id: team-factorName-timestamp
    _id_parts = [team_name, factor_label, evaluation_date]

    # Compose info string: list each (student or metric, value, weights)
    metric_info_parts = []
    for metric_name, tuples in intermediate_metric_values.items():
        for student, val in tuples:
            # if student name is None, we use the mretrics name
            label = student if student is not None else metric_name
            metric_info_parts.append(
                f"('{label}', value: {val}, weights: {factor_def.get('weights', [])})"
            )
    metric_info = "; ".join(metric_info_parts)
    
    info_lines = f"metrics:{ {metric_info} }, formula: {factor_def['formula']}, value: {final_value}"
    

    # Part of the mongo document that does not change
    static = {
        "name"         : factor_def['name'],
        "description"  : factor_def['description'],
        "project"      : team_name,
        "factor"       : factor_label,
    }

    # Part of the mongo document that will change each time there is an event
    dynamic = {
        "evaluationDate": evaluation_date,
        "value"        : final_value,
        "info"         : info_lines
    }
    
 
     # Insert into MongoDB, with the dynamic and static parts, upserting or inserting
    collection.update_one(
        {"_id": "_".join(_id_parts)},
        {
            "$set": dynamic,
            "$setOnInsert": static
            },
        upsert=True        
        )


