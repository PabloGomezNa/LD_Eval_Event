# metriclogic/recalc.py
import os
from pymongo import MongoClient
from metriclogic.metric_placeholder import load_query_template, replace_placeholders_in_query
from metriclogic.store_metric_mongo import store_metric_result
from metriclogic.run_mogo_query import run_mongo_query_for_metric, evaluate_formula
from statistics import pstdev



import logging

logging.basicConfig(
    level=logging.INFO,  # Set level to DEBUG so that all debug and above messages are shown
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__) 


'''
TODO:

EVERYTHING MORE PRETTY, DELETE THE PRINTS, ADD LOGGING, ADD EXCEPTIONS, TESTS, ETC.
DELETE USELESS STUFF

HADNLE STANDARD DEVIATION METRICS

MOVE THINGS TO .ENV

'''



    
    
    
    
    

    
    
    
    





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
    logger.info(f"param_map: {param_map}")
    doc = run_mongo_query_for_metric(team_name, student_name, query_file, event_type, param_map)
    logger.info(f"doc: {doc}")
    if not doc:
        final_val=0.0
        print(f"No aggregator resutsl, setting final_val to 0.0")
    else:
        #evaulate the formula
        final_val=evaluate_formula(formula_str,doc)
    print(f"Result: {final_val}\n")
    
    store_metric_result(team_name, metric_def["name"], scope="individual", final_val=final_val, event_type=event_type, student_name=student_name, aggregator_doc=doc)
    



def compute_metric_for_team(metric_def, event_type, team_name,students):
    """
    A simpler approach if no placeholders needed, or if placeholders are at team level.
    """
    
        #Un poco feo pero sirve
    if event_type == "push":
        collection_name = f"{team_name}_commits" 
    elif event_type == "issue":
        collection_name = f"{team_name}_issue"
    elif event_type == "task":
        collection_name = f"{team_name}_tasks"
    elif event_type == "epic":
        collection_name = f"{team_name}_epic"
    elif event_type in ["userstory", "relateduserstory"]:
        collection_name = f"{team_name}_userstory"
        
    basepath = os.path.splitext(metric_def["filePath"])[0]
    query_file = basepath + ".query"
    formula_str = metric_def["formula"]
    
    
    if formula_str in ["stdevCommits", "stdevTasks"]:
        return compute_team_sd_metric(metric_def, event_type, team_name, collection_name, students)
    
    else:
        
        print(f"Recomputing TEAM metric '{metric_def['name']}' formula=({formula_str}) for team='{team_name}'")
        
        param_map={} #Empty param map as we are not using any placeholders in any team query
        pipeline = load_query_template(query_file)
        pipeline = replace_placeholders_in_query(pipeline, param_map)

        
        client = MongoClient("mongodb://localhost:27017")
        db = client["event_dashboard"]
        results = list(db[collection_name].aggregate(pipeline))
        logger.info(f"pipeline: {pipeline}") #REMOVED LATER, ONLY TO LOG
        logger.info(f"db collection name: {collection_name}") #REMOVED LATER, ONLY TO LOG
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
    


def compute_team_sd_metric(metric_def, event_type, team_name, collection_name, team_members=None):
    """
    Special case when we calculate standard deviation for a team metric.
    """
    basepath = os.path.splitext(metric_def["filePath"])[0]
    query_file = basepath + ".query"

    print(f"[TEAM-SD] Recomputing metric '{metric_def['name']}' for team='{team_name}'")


    # load aggregator
    pipeline = load_query_template(query_file)

    client = MongoClient("mongodb://localhost:27017")
    db = client["event_dashboard"]
    docs = list(db[collection_name].aggregate(pipeline))
    print(f"Aggregator results: {docs}")

    # build aggregator_map
    aggregator_map = {}
    for d in docs:
        user = d["_id"]
        aggregator_map[user] = d["count"]

    # if we have no team_members, set an empty list
    if not team_members:
        team_members = []

    # create the list of counts, to account for user that do not have a ny task/commit 
    
    commitsTotal=sum(aggregator_map.values()) # total number of commits/tasks
    fractions = [
    aggregator_map.get(member, 0) / commitsTotal for member in team_members
]

    # compute stdev
    if len(fractions) > 1:
        final_val = pstdev(fractions)
    else:
        final_val = 0.0

    aggregator_doc = {
        "perUserCounts": aggregator_map,
        "teamMembers": team_members
    }

    store_metric_result(
        team_name=team_name,
        metric_name=metric_def["name"],
        scope="team",
        final_val=final_val,
        event_type=event_type,
        aggregator_doc=aggregator_doc
    )

    print(f"[TEAM-SD] Final stdev: {final_val}\n")
    return final_val






