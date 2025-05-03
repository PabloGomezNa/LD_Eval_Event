from factors_logic.store_factors_mongo import store_factor_result
from pymongo import MongoClient

def latest_indicator_value(db, team, factor_name, student=None):
    coll = db[f"{team}_factors"]
    
    
    #doc = coll.find_one(criteria, sort=[('_id', -1)])
    doc = coll.find_one({'metric': metric_name})
        
    if doc is None: #if no document found, return empty list
        return [(None, 0.0)]
    
    
    if 'student_name' in doc: #means we have one individual value per student
        
        #AQUI TODOS LOS ESTUDIANTES TENDRAN METRRICAS INDIVIDUALES, AUNQUE NO HAYAN HECHO NADA, POR QUE SE ENCARGA EL METRICS DE HACER UN LOOP EN TODOS LOS ESTUDIANTES
        pipeline = [
            {'$match': {'metric': metric_name}},
            {'$sort':  {'student_name': 1, 'evaluationDate': -1}},
            {'$group': {'_id': '$student_name',
                        'latest': {'$first': '$value'}}}
        ]
        return [(doc['_id'], doc['latest']) for doc in coll.aggregate(pipeline)]
    
    
    # If its a team metric, only one per team, we find it and return it as is
    doc = coll.find_one({'metric': metric_name},
                        sort=[('evaluationDate', -1)])
        
    
    return [(None, doc['value'])] if doc else []



# ── factor computation ───────────────────────────────────────────────────────
def compute_indicator(factor_def, values_dict):
    """
    `values_dict`  {metric_name: list_of_numbers}
    Supports 'average' and 'weighted_average'.
    """
    # 1.  flatten everything   --------------------------
    flat_vals   = []
    flat_metric = []          # parallel list remembering which metric produced each val
    flat_student = []        # parallel list remembering which student produced each val
    
    for m, tup_list in values_dict.items():
        for student, val in tup_list:
            flat_vals.append(val)           # List of all the values
            flat_metric.append(m)       # List of the names of the metrics that compose the factors
            flat_student.append(student) #List of the students names in case the factor uses an individual metric
    
    print(f"flat_vals: {flat_vals}")
    print(f"flat_metric: {flat_metric}")
    print(f"flat_student: {flat_student}")
    
    if not flat_vals:           # metric not stored yet
        return 0.0, "no input"

    op = factor_def.get('operation', 'average')

    # 2.  ordinary average     --------------------------
    if op == 'average':
        res = sum(flat_vals)/len(flat_vals)
        info = f"avg({flat_vals})"

    # 3.  weighted average     --------------------------
    elif op == 'weighted_average':
        base_w = [float(w) for w in factor_def.get('weights', [])]
        if not base_w or len(base_w) != len(factor_def['metric']):
            base_w = [1.0]*len(factor_def['metric'])

        # replicate each metric-weight for every student value
        metric2weight = dict(zip(factor_def['metric'], base_w))
        w_expanded    = [metric2weight[m] for m in flat_metric]

        res  = sum(v*w for v, w in zip(flat_vals, w_expanded)) / sum(w_expanded)
        info = f"w_avg({list(zip(flat_metric, flat_vals, w_expanded))})"

    else:
        raise ValueError(f"Unknown operation '{op}'")

    return res, info



