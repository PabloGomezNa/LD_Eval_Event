# metriclogic/recalc.py
import os
import json

from pymongo import MongoClient
import json
from metriclogic.metric_placeholder import load_query_template, replace_placeholders_in_query

def compute_metric_for_student(metric_def, student_name, team):
    """
    Example function to compute an *individual* metric for a single student.
    1) We'll read the .query JSON (matching .properties base filename).
    2) Replace placeholders like $$studentUser => student_name
    3) Execute the query in ES (stubbed).
    4) Possibly apply the formula from .properties (like tasksAssignee / tasksTotal).
    5) Store the result somewhere.
    """
    
    basepath = os.path.splitext(metric_def["filePath"])[0]  # strip ".properties"
    query_file = basepath + ".query"
    if not os.path.isfile(query_file):
        print(f"No .query file found at {query_file}, skipping.")
        return

    # load the .query
    query_ast = load_query_template(query_file)

    # placeholders
    param_map = { "$$studentUser": student_name }
    # e.g. if we also want $$team => "ASW_Team5", do param_map["$$team"] = team

    final_query_ast = replace_placeholders_in_query(query_ast, param_map)
    print(f"Recomputing INDIV metric '{metric_def['name']}' for student='{student_name}' team='{team}'")
    # run the final_query_ast in ES or DB...
    result = compute_commits_metric(team_name=team, student_name=student_name, query_file=query_file)
    # parse result, do formula from .properties

    # do something with the final metric value
    # ...
    # print("Query would be: ", json.dumps(final_query_ast, indent=2))


def compute_metric_for_team(metric_def, team):
    """
    A simpler approach if no placeholders needed, or if placeholders are at team level.
    """
    basepath = os.path.splitext(metric_def["filePath"])[0]
    query_file = basepath + ".query"
    if not os.path.isfile(query_file):
        print(f"No .query file found at {query_file}, skipping.")
        return

    query_ast = load_query_template(query_file)
    # If you also want $$team placeholders, do it here
    final_query_ast = query_ast  # or a replace if needed
    print(f"Recomputing TEAM metric '{metric_def['name']}' for team='{team}'")
    # print("   (Stub) Query would be: ", json.dumps(final_query_ast, indent=2))
    # run the final_query_ast in ES or DB...




def run_mongo_query_for_metric(team_name, student_name, query_file):
    """
    1) Derive the right collection name for this team
    2) Load .query (an aggregation pipeline) from disk
    3) Insert placeholders (e.g. $$studentUser => "alice") if needed
    4) Run the aggregation
    5) Return commitsTotal, commitsAssignee
    """
    # E.g. if you keep separate collections like "Team_A_commits", do:
    collection_name = f"{team_name}_commit"
    print(collection_name)
    
    # load the aggregator pipeline from your .query file
    with open(query_file, "r", encoding="utf-8") as f:
        pipeline = json.load(f)

    # If your .query has placeholders like "$$studentUser", you need a small
    # function to recursively replace them, similar to previous examples.
    pipeline = replace_placeholders_in_query(pipeline, {
        "$$studentUser": student_name
    })

    # connect to mongo, run the pipeline
    client = MongoClient("mongodb://localhost:27017")
    #the database is called event_dashboard
    db = client["event_dashboard"]
    cursor = db[collection_name].aggregate(pipeline)
    results = list(cursor)
    print(f"Results: {results}")

    if not results:
        # no data
        return (0, 0)  # or something to indicate no data

    doc = results[0]
    commits_assignee = doc.get("commitsAssignee", 0)
    commits_total = doc.get("commitsTotal", 0)
    return (commits_assignee, commits_total)

def compute_commits_metric(team_name, student_name, query_file):
    """
    Actually compute commitsAssignee/commitsTotal using the aggregator result.
    """
    commits_assignee, commits_total = run_mongo_query_for_metric(
        team_name, student_name, query_file
    )
    if commits_total == 0:
        return 0.0
    return commits_assignee / commits_total

# def example_usage():
#     metric_value = compute_commits_metric(
#         team_name="LDTestOrganization",
#         #student_name="PabloGomezNa",
#         student_name="PepitoGomezNa",
#         query_file="metrics/commits_Student.query"
#     )
#     print(f"Final metric => {metric_value}")



# if __name__ == "__main__":
#     example_usage()
