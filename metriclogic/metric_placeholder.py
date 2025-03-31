# metriclogic/placeholders.py
import json

def load_query_template(query_file):
    """
    Loads the .query file as a Python object (list/dict).
    """
    with open(query_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# placeholders
def replace_placeholders_in_query(query_ast, param_map):
    """
    If your .query references $$studentUser or $$team, do string-replace.
    """
    if isinstance(query_ast, dict):
        return {
            k: replace_placeholders_in_query(v, param_map)
            for k,v in query_ast.items()
        }
    elif isinstance(query_ast, list):
        return [
            replace_placeholders_in_query(item, param_map)
            for item in query_ast
        ]
    elif isinstance(query_ast, str):
        out_str = query_ast
        for placeholder, real_value in param_map.items():
            out_str = out_str.replace(placeholder, real_value)
        return out_str
    else:
        return query_ast