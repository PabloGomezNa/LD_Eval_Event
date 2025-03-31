# metriclogic/recalc.py
import os
import json
from pymongo import MongoClient
from metriclogic.metric_placeholder import load_query_template, replace_placeholders_in_query
from datetime import datetime

'''
TODO:

EVERYTHING MORE PRETTY, DELETE THE PRINTS, ADD LOGGING, ADD EXCEPTIONS, TESTS, ETC.
DELETE USELESS STUFF

HADNLE STANDARD DEVIATION METRICS

MOVE THINGS TO .ENV

'''


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
    
    print(f"[store_metric_result] Inserted doc: {doc}")
    
    
    
    
def evaluate_formula(formula_str, result_doc):
    """
    Explanation
    """
    # create a variable dict with all keys from the doc
    # e.g. commitsAssignee -> 10, commitsTotal -> 11
    local_vars = {}
    
    #Scan the result_doc and create a dictionary with the values of the keys
    for k, v in result_doc.items(): 
        if isinstance(v, (int, float)): # if the value is a number, we can use it directly
            local_vars[k] = float(v) # convert to float for safety
        else: # if the value is not a number, we can skip it or set it to 0.0
            local_vars[k] = 0.0  
            
            
    # Now evaluate the expression
    try:
        ## Use eval to evaluate the formula string with the local_vars as context
        value = eval(formula_str, {}, local_vars) #eval takes a string expression and "transforms" it into a python expression that can be calculated
    except ZeroDivisionError: # handle division by zero
        value = 0.0
    except Exception as e: # handle any other exceptions giving the error and set to 0
        print(f"[evaluate_formula] Error: {e}, defaulting to 0.0")
        value = 0.0
    return value
    
    
    
    
def run_mongo_query_for_metric(team_name: str, student_name: str, query_file: str, event_type, placeholder_map: dict) -> dict:
    """
    Explanation
    """
    
    # #possible related_events sent by LD_connect from GITHUB: push, issues       from TAIGA: issue, epic, task, userstory, relatedusertory



    #First get the collection we will use to run the query and get the data
    if event_type == "push":
        collection_name = f"{team_name}_commits" 
    elif event_type == "issue":
        collection_name = f"{team_name}_issue"
    elif event_type == "task":
        collection_name = f"{team_name}_task"
    elif event_type == "epic":
        collection_name = f"{team_name}_epic"
    elif event_type in ["userstory", "relateduserstory"]:
        collection_name = f"{team_name}_userstory"


    # load the aggregator pipeline from the .query file    
    pipeline = load_query_template(query_file) 
    # .query has placeholders  "$$studentUser", need the function to recursively replace them
    pipeline = replace_placeholders_in_query(pipeline, {"$$studentUser": student_name})

    # connect to mongo, run the pipeline
    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]
    cursor = db[collection_name].aggregate(pipeline)
    results = list(cursor)
    print(f"Results: {results}") #REMOVED LATER, ONLY TO LOG

    if not results: #if for some case the query returns no results, we return 0,0 
        return {} 

    doc = results[0]
    
    return doc








def compute_metric_for_student(metric_def, event_type, student_name, team_name):
    """
    Expalanation
    """
    
    basepath = os.path.splitext(metric_def["filePath"])[0]  # strip ".properties" #HERE WE WILL PUT IT IN .ENV LATER
    query_file = basepath + ".query"


    
    formula_str = metric_def["formula"]  # e.g. "commitsAssignee / commitsTotal"
    print(f"Recomputing INDIV metric '{metric_def['name']}' formula=({formula_str}) "
          f"for student='{student_name}' team='{team_name}'")
    

    # placeholders, will replace $$studentUser with the student name
    param_map = { "$$studentUser": student_name }
    doc = run_mongo_query_for_metric(team_name, student_name, query_file, event_type, param_map)

    if not doc:
        final_val=0.0
        print(f"No aggregator resutsl, setting final_val to 0.0")
    else:
        #evaulate the formula
        final_val=evaluate_formula(formula_str,doc)
    print(f"Result: {final_val}\n")
    
    store_metric_result(team_name, metric_def["name"], scope="individual", final_val=final_val, event_type=event_type, student_name=student_name, aggregator_doc=doc)
    



def compute_metric_for_team(metric_def, event_type, team_name):
    """
    A simpler approach if no placeholders needed, or if placeholders are at team level.
    """
    
        #Un poco feo pero sirve
    if event_type == "push":
        collection_name = f"{team_name}_commits" 
    elif event_type == "issue":
        collection_name = f"{team_name}_issue"
    elif event_type == "task":
        collection_name = f"{team_name}_task"
    elif event_type == "epic":
        collection_name = f"{team_name}_epic"
    elif event_type in ["userstory", "relateduserstory"]:
        collection_name = f"{team_name}_userstory"
        
    basepath = os.path.splitext(metric_def["filePath"])[0]
    query_file = basepath + ".query"
    formula_str = metric_def["formula"]
    
    print(f"Recomputing TEAM metric '{metric_def['name']}' formula=({formula_str}) for team='{team_name}'")
    
    param_map={}

    pipeline = load_query_template(query_file)
    pipeline = replace_placeholders_in_query(pipeline, param_map)

    



    
    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]
    results = list(db[collection_name].aggregate(pipeline))
    print(f"Results from aggregator: {results}")

    if not results:
        final_val = 0.0
        print(f"No aggregator result; defaulting to {final_val}")
        doc = {} # If no results, we can set doc to empty dict or None
    else:
        # 3) Evaluate the formula
        doc = results[0]   # aggregator typically returns one doc
        final_val = evaluate_formula(formula_str, doc)

    print(f"TEAM metric result: {final_val}\n")

    store_metric_result( team_name=team_name, metric_name=metric_def["name"], scope="team", final_val=final_val, event_type=event_type, aggregator_doc=doc)
    








