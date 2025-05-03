import os
from collections import defaultdict
from utils.quality_model_loader import scan_quality_model_folder


def load_required_fields_metrics(filepath):
    """
    Reads some keys from the .properties metrics files. Returns a dict with those fields
    if found, ignoring everything else.
    """
    allowed_keys = {'name', 'relatedEvent', 'scope', 'metric','description','factors','weights'}
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


def build_metric_def(props, qm, path):
    return {
        "filePath": path,
        "name": props["name"],
        "scope": props.get("scope", "team"),
        "formula": props["metric"],
        "params": props.get("params", {}),
        "description": props.get("description", ""),
        "factors": [x.strip() for x in props.get("factors","").split(",") if x],
        "weights": [float(w) for w in props.get("weights","").split(",") if w],
        "quality_model": qm,
    }

def build_metrics_index_per_qm(qm_root="QUALITY_MODELS"):
    return scan_quality_model_folder(
        qm_root,
        subfolder="metrics",
        props_loader=load_required_fields_metrics,
        build_def=build_metric_def
    )
    

# def build_metrics_index_per_qm(metrics_root='metrics'):
#     """
#     Devuelve:
#       ALL_METRICS_BY_QM = { 'AWS': [...], 'AMEP': [...], ... }
#       EVENT_MAP_BY_QM   = { 'AWS': { 'push':[...], ...}, 'AMEP': {...}, ... }
#     """
#     all_by_qm   = {}
#     event_by_qm = {}

#     for qm in os.listdir(metrics_root):
#         full_dir = os.path.join(metrics_root, qm)
#         if not os.path.isdir(full_dir):
#             continue    # ignora README, etc.

#         all_m = []
#         evt_m = defaultdict(list)

#         for root, _, files in os.walk(full_dir):
#             for f in files:
#                 if not f.endswith('.properties'):
#                     continue
#                 props = load_required_fields_metrics(os.path.join(root, f))
#                 metric_def = {
#                     'filePath' : os.path.join(root, f),
#                     'name'     : props['name'],
#                     'scope'    : props.get('scope', 'team'),
#                     'formula'  : props['metric'],
#                     'params'   : props.get('params', {}),
#                     'description': props.get('description',''),
#                     'factors'  : [x.strip() for x in props.get('factors','').split(',') if x],
#                     'weights'  : [float(w) for w in props.get('weights','').split(',') if w],
#                     'quality_model': qm                                
#                 }
#                 all_m.append(metric_def)
#                 for evt in [e.strip() for e in props['relatedEvent'].split(',')]:
#                     evt_m[evt].append(metric_def)

#         all_by_qm[qm.lower()]   = all_m
#         event_by_qm[qm.lower()] = dict(evt_m)

#     return all_by_qm, event_by_qm