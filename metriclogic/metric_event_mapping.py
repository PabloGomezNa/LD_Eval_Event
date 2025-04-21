import os
from collections import defaultdict



def load_required_fields(filepath):
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




def build_metrics_index(metrics_root='metrics'): #THIS ROOT WILL BE LATER IN THE .ENV FILE
    """
    Recursively scan `metrics_root` for .properties files.
    Return two maps:
      - all_metrics: list of all metric definitions
      - event_to_metrics: dict { event -> [metricDef1, metricDef2, ...] }
    """
    all_metrics = []
    event_to_metrics = defaultdict(list)

    for root, dirs, files in os.walk(metrics_root):
        for file in files:
            if file.endswith('.properties'):
                fullpath = os.path.join(root, file)
                props = load_required_fields(fullpath)
                
                # We expect metric "name" to be mandatory
                metric_name = props.get('name', os.path.splitext(file)[0])

                # Extract description
                description = props.get('description', '')
                
                #Extract factors 
                factors = [f.strip() for f in props.get("factors", "").split(",") if f],
                #extract weights, must store all the weights in an array                 
                weights = [float(w) for w in props.get("weights", "").split(",") if w]
                
                # Extract events
                related_events = props.get('relatedEvent', '')
                events = [evt.strip() for evt in related_events.split(',') if evt.strip()]

                # Extract the scope
                scope = props.get('scope', '')  # default to "team" if not specified

                # Extract the formula
                formula = props.get('metric', '')              
                
                
                # Now build a dictionary describing the metric
                metric_def = {
                    'filePath': fullpath,
                    'name': metric_name,
                    'description': description,
                    'factors': factors,
                    'weights': weights,
                    'scope': scope,
                    'formula': formula, 
                    'params': props.get('params', {}),  # Add parameters if any
                }

                all_metrics.append(metric_def)

                # For each event in events, add to event->metricDef lista
                for evt in events:
                    event_to_metrics[evt].append(metric_def)

    return all_metrics, dict(event_to_metrics)


