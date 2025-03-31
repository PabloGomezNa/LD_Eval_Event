import os
from collections import defaultdict

def load_required_fields(filepath):
    """
    Reads only the 'name', 'relatedEvent', and 'scope' keys
    from a .properties file. Returns a dict with those fields
    if found, ignoring everything else.
    """
    allowed_keys = {'name', 'relatedEvent', 'scope'}
    props = {}
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

    return props

def build_metrics_index(metrics_root='metrics'):
    """
    Recursively scan `metrics_root` for .properties files.
    Return:
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

                # Extract events
                related_events = props.get('relatedEvent', '')
                events = [evt.strip() for evt in related_events.split(',') if evt.strip()]

                # Extract scope
                scope = props.get('scope', '')  # default to "team" if not specified

                # Now build a dictionary describing the metric
                metric_def = {
                    'filePath': fullpath,
                    'name': metric_name,
                    'scope': scope,
                    'properties': props  # everything else
                }

                all_metrics.append(metric_def)

                # For each event in events, add to event->metricDef list
                for evt in events:
                    event_to_metrics[evt].append(metric_def)

    return all_metrics, dict(event_to_metrics)


