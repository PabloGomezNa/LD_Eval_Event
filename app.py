# app.py

import threading
from flask import Flask, request, jsonify

# We'll import your existing code
from metriclogic.metric_event_mapping import build_metrics_index
from LearningDashboardAPIREST_Call.StudentDatafromLDRESTAPI import build_team_students_map
from metriclogic.metric_recalculation import compute_metric_for_student, compute_metric_for_team

from utils.load_config_file import get_event_meta


app = Flask(__name__)

# Build the metrics event map at startup (like you did in main.py before)
ALL_METRICS, EVENT_MAP = build_metrics_index()

# Build the team->students map at startup
TEAM_STUDENTS_MAP = build_team_students_map()



def background_process_event(event_data):


    event_type = event_data.get("event_type")
    team_name = event_data.get("team_name")


    meta = get_event_meta(event_type)
    print(meta)
    
    if not team_name:
        print("[Warning] No 'team_name' found in event_data, skipping.")
        return    


    data_source= meta["data_source"]
    students=TEAM_STUDENTS_MAP.get(team_name, {}).get(data_source, [])
    
    
    # #ESTO LO CAMBIAREMOS PARA QUE SEA LEIDO POR EL ARCHIVO .CONDIF
    # if event_type in ["push", "pull_request"]:  #events from GitHub
    #     students = data_for_team.get("GITHUB", [])
    # else:
    #     # For instance, "issue", "task" from Taiga
    #     students = data_for_team.get("TAIGA", [])






        
    # Retrieve the students for that team
    print(f"[Background] event={event_type}, team={team_name}, students={students}")

    # Retrieve the triggered metrics
    triggered_metrics = EVENT_MAP.get(event_type, [])
    print(f"[Background] triggered metrics: {[m['name'] for m in triggered_metrics]}")

    # Recompute each metric
    for metric_def in triggered_metrics:
        scope = metric_def["scope"]
        if scope == "individual":
            for student_name in students:
                compute_metric_for_student(metric_def, event_type, student_name, team_name)
        else:  # scope == "team"
            compute_metric_for_team(metric_def, event_type, team_name,students)

    print("[Background] Done processing event.")





@app.route("/api/event", methods=["POST"])
def handle_event():
    """
    HTTP endpoint that:
    1) receives a JSON body with event_type + team_name + ...
    2) immediately returns 200
    3) spawns a background thread to do metric recalculation
    """
    event_data = request.get_json(force=True)
    # Spawn a background thread
    t = threading.Thread(target=background_process_event, args=(event_data,))
    t.start()

    return jsonify({"status": "received"}), 200

def run_app():
    # Runs the Flask app
    app.run(host="0.0.0.0", port=5001, debug=True)

