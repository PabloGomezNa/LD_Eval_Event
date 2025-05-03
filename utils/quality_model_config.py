# utils/quality_model_config.py
import json

def load_qualitymodel_map(path="quality_models_teams_config.json"):
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    #  {'aws': ['AMEP11Beats', ...], ... }  →  {'AMEP11Beats':'aws', ...}
    return {team: qm.lower() for qm, teams in raw.items() for team in teams}


def choose_qualitymodel(external_id, explicit_qm, qm_map):
    if explicit_qm:
        return explicit_qm.lower()
    return qm_map.get(external_id, "default")