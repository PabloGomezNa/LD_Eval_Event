
import os
from collections import defaultdict
from utils.quality_model_loader import scan_quality_model_folder


def load_required_fields_factor(filepath):
    """
    Reads some keys from the .properties metrics files. Returns a dict with those fields
    if found, ignoring everything else.
    
    I THINK WE CAN DELETE ALL THE PARAMS LOGIC, AS IN INDICATOR AND FACTORS WE WONT HAVE
    
    
    
    ALSO DELTE THE FACTORS AS WE CAN GET AND USE THE NAME OF THE FILE
    """ 
    
    allowed_keys = {'name', 'description','metric','formula','weights','relatedEvent'}
    props = {}
    params = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if key in allowed_keys:
                props[key] = value

            elif key.startswith('param.'):
                raw = value.strip() #Get the value of the parameter
                try:                     # turn to int/float if we can
                    val = int(raw) if raw.isdigit() else float(raw)
                except ValueError: #if not a number, keep it as string
                    val = raw
   
                params[key[6:]] = val
                
        if params:
            props['params'] = params
                
    return props


def build_factor_def(props, qm, path):
    return {
        "filePath": path,
        "name": props["name"],
        "description": props.get("description",""),
        "metric": [m.strip() for m in props.get("metric","").split(",") if m],
        "formula": props.get("formula", "average"),
        "weights": [w.strip() for w in props.get('weights', '').split(',') if w.strip()],
        "quality_model": qm,
    }

def build_factors_index_per_qm(qm_root="QUALITY_MODELS"):
    return scan_quality_model_folder(
        qm_root,
        subfolder="factors",
        props_loader=load_required_fields_factor,
        build_def=build_factor_def
    )
    
    

# def build_factors_index_per_qm(factors_root='factors'):
#     """Return: (ALL_FACTORS, EVENT_TO_FACTORS)"""
    
    
#     all_by_qm   = {}
#     event_by_qm = {}

#     # Loop trough all the subfolders of factors_root
#     for qm in os.listdir(factors_root):
#         full_dir = os.path.join(factors_root, qm)
#         if not os.path.isdir(full_dir):
#             continue    # if we find anything that is not a folder, we skip it

#         factors_list = []
#         evt_map = defaultdict(list)

#         # Search for all the .properties files in the folder and subfolders
#         for root, _, files in os.walk(full_dir):
#             for fname in files:
#                 if not fname.endswith('.properties'):
#                     continue
#                 full_path = os.path.join(root, fname)
#                 props = load_required_fields_factor(full_path)

#                 # Define the factor
#                 fdef = {
#                     'filePath'     : full_path,
#                     'name'         : props['name'],
#                     'description'  : props.get('description', ''),
#                     'metric'       : [m.strip() for m in props.get('metric', '').split(',') if m.strip()],
#                     'operation'    : props.get('operation', 'average'),
#                     'weights'      : [w.strip() for w in props.get('weights', '').split(',') if w.strip()],
#                     'quality_model': qm.lower(),
#                 }
#                 factors_list.append(fdef)

#                 # Map the event to the factor
#                 for evt in props.get('relatedEvent', '').split(','):
#                     evt = evt.strip()
#                     if evt:
#                         evt_map[evt].append(fdef)

#         all_by_qm[qm.lower()]   = factors_list
#         event_by_qm[qm.lower()] = dict(evt_map)

#     return all_by_qm, event_by_qm