from factors_logic.store_factors_mongo import store_factor_result
from database.mongo_client import get_collection


def latest_metric_value(team: str, metric_name: str, student: str = None)-> list:
    '''
    Retrieve the latest metric value(s) from MongoDB for a given metric.
    '''

    coll = get_collection(f"{team}_metrics")
    
    # Try finding any document for this metric
    doc = coll.find_one({'metric': metric_name})
    if doc is None: 
        #if no document found, return empty list
        return [(None, 0.0)]
    
    # If individual-student metric (doc contains student_name field)
    if 'student_name' in doc: 
        # We create a pipeline to get the latest value for each student
        pipeline = [
            {'$match': {'metric': metric_name}},
            {'$sort':  {'student_name': 1, 'evaluationDate': -1}},
            {'$group': {'_id': '$student_name',
                        'latest': {'$first': '$value'}}}
        ]
        # Return list of ("metric_student", latest)
        return [(f"{metric_name}_"+doc['_id'], doc['latest']) for doc in coll.aggregate(pipeline)]
        # For instance: {'closedtasks_Student': [('closedtasks_Student_pablogz5', 0.0), ('closedtasks_Student_Charlie55', 0.0), ('closedtasks_Student_pgomezn', 0.5)]}
    
    # Otherwise team-level, return single latest value
    doc = coll.find_one({'metric': metric_name}, sort=[('evaluationDate', -1)])
    return [(None, doc['value'])] if doc else []



def compute_factor(team_name: str, factor_def: dict, values_dict: dict)-> tuple:
    """
    Compute a factor's final value based on its constituent metric values.
    Supports 'average' and 'weighted_average' operations.
    """
    # Loop over the values_dict to get the values, the metric names and students
    flat_vals   = []
    flat_metric = []          
    flat_student = []       
    
    # Loop over the values_dict to get the values, the metric names and students
    for m, tup_list in values_dict.items():
        for student, val in tup_list:
            flat_vals.append(val)           # List of all the values
            flat_metric.append(m)       # List of the names of the metrics that compose the factors
            flat_student.append(student) #List of the students names in case the factor uses an individual metric
    
    # No data return 0.0 and "no input"
    if not flat_vals:           
        return 0.0, "no input"

    # Get the operation to be performed from the factor definition
    op = factor_def.get('formula', 'average')

    # Calculate the final value based on the weighted average
    if op == 'average':
        final_val = sum(flat_vals)/len(flat_vals)
        info = f"avg({flat_vals})"

    # Calculate the final value based on the weighted average
    elif op == 'weighted_average':
        base_w = [float(w) for w in factor_def.get('weights', [])]
        if not base_w or len(base_w) != len(factor_def['metric']):
            base_w = [1.0]*len(factor_def['metric'])

        # Replicate each metric-weight for every student value
        metric2weight = dict(zip(factor_def['metric'], base_w))
        w_expanded    = [metric2weight[m] for m in flat_metric]

        final_val  = sum(v*w for v, w in zip(flat_vals, w_expanded)) / sum(w_expanded)
        info = f"w_avg({list(zip(flat_metric, flat_vals, w_expanded))})"

    else:
        raise ValueError(f"Unknown operation '{op}'")

    #Store the factor result in the mongo database
    store_factor_result(team_name=team_name, factor_def=factor_def, final_value=final_val,  intermediate_metric_values=values_dict)
    
    return final_val, info



