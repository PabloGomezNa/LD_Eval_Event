# app.py

import threading
from flask import Flask, request, jsonify
import logging
import os 

from metrics_logic.metric_event_mapping import build_metrics_index_per_qm
from metrics_logic.metric_recalculation import compute_metric_for_student, compute_metric_for_team

from factors_logic.factor_event_mapping import build_factors_index_per_qm
from factors_logic.factor_recalculation import compute_factor, latest_metric_value

from indicators_logic.indicator_event_mapping import build_indicators_index_per_qm
from indicators_logic.indicator_recalculation import compute_indicator, latest_factor_value

from utils.load_config_file import get_event_meta
from utils.logger_setup import setup_logging
from utils.StudentDatafromLDRESTAPI import build_team_students_map
from utils.quality_model_config import load_qualitymodel_map, choose_qualitymodel


setup_logging()
logger = logging.getLogger(__name__)



QUALITY_MODELS_DIR = os.getenv("QUALITY_MODELS_DIR", "QUALITY_MODELS")

app = Flask(__name__)

# Build the metrics event map at startup scaning all the quality models metrics subfolders
ALL_METRICS_BY_QM,  EVENT_METRICS_BY_QM  = build_metrics_index_per_qm(QUALITY_MODELS_DIR)

# Build the metrics event map at startup scaning all the quality models factors subfolders
ALL_FACTORS_BY_QM,  EVENT_FACTORS_BY_QM  = build_factors_index_per_qm(QUALITY_MODELS_DIR)

# Build the metrics event map at startup scaning all the quality models indicators subfolders
ALL_INDICATORS_BY_QM,  EVENT_INDICATORS_BY_QM  = build_indicators_index_per_qm(QUALITY_MODELS_DIR)

# Build the team->students map at startup
TEAM_STUDENTS_MAP = build_team_students_map()
TEAM_QUALITYMODEL_MAP = load_qualitymodel_map()



def background_process_event(event_data):

    event_type = event_data.get("event_type")
    external_id = event_data.get("prj")
    author_name = event_data.get("author_login")
    
    #If there is no quality model, we assume it is the default one
    quality_model_in_query = (event_data.get("quality_model"))
    quality_model = choose_qualitymodel(external_id, quality_model_in_query, TEAM_QUALITYMODEL_MAP)
    
    if not external_id:
        logger.warning("No 'team_external_id' found in event_data, skipping.")
        return    

    # Using the sources_config.json file, we extract the data source for the event type
    meta = get_event_meta(event_type)
    
    # Retrieve the students for that team with the corresponding data source
    data_source= meta["data_source"]
    students=TEAM_STUDENTS_MAP.get(external_id, {}).get(data_source, [])
    logger.info(f"Event={event_type}, team with external_id={external_id}, students={students}, quality_model={quality_model}")



    # RECALCULTION OF THE METRICS
    # Retrieve the triggered metrics for the quality model
    triggered_metrics = EVENT_METRICS_BY_QM.get(quality_model, {}).get(event_type, {})
    logger.info(f"Triggered metrics: {[m['name'] for m in triggered_metrics]}")

    # Recompute each metric
    for metric_def in triggered_metrics:
        scope = metric_def["scope"]
        if scope == "individual":
            for student_name in students:
                compute_metric_for_student(metric_def, event_type, student_name, team_name=external_id)
        elif scope == "team":  # scope == "team"
            compute_metric_for_team(metric_def, event_type, team_name=external_id,students=students)
        else: #scope == "individual_only"
            compute_metric_for_student(metric_def, event_type, author_name, team_name=external_id)
    


    # RECALCULTION OF THE FACTORS
    triggered_factors = EVENT_FACTORS_BY_QM.get(quality_model, {}).get(event_type, [])
    logger.info(f"Triggered factors: {[f['name'] for f in triggered_factors]}")
        
    for factor_def in triggered_factors:
        values= {} # Empty dictionary to store the values for each metric in the factor
        
        for metrics in factor_def["metric"]:
            #For each metric in the factor, we need to get the latest value for that metric
            # We need to store these values in a dictionary with the metric name as key and the value as value
            values[metrics] = latest_metric_value(external_id, metrics)
        
        logger.info(f"Values of the metrics of factor {factor_def['name']}: {values}")
        final_val= compute_factor(factor_def, values, external_id)



    # RECALCULTION OF THE INDICATORS
    triggered_indicators = EVENT_INDICATORS_BY_QM.get(quality_model, {}).get(event_type, [])
    logger.info(f"Triggered factors: {[f['name'] for f in triggered_indicators]}")
    # logger.info(f"Triggered indicators: {[i['name'] for i in triggered_indicators]}")
        
    # for indicator_def in triggered_indicators:
    #     values= {} # Empty dictionary to store the values for each metric in the factor
        
    #     for factor in indicator_def["factor"]:
    #         #For each metric in the factor, we need to get the latest value for that metric
    #         # We need to store these values in a dictionary with the metric name as key and the value as value
    #         values[indicator] = latest_factor_value(external_id, factor)
        
    #     logger.info(f"Values of the factor of indicator {indicator_def["name"]}: {values}")
    #     final_val= compute_indicator(indicator_def, values, external_id)

    
    logger.info("Done processing event.")





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

