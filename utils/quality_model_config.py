# utils/quality_model_config.py
import json

def load_qualitymodel_map(path: str = "quality_models_teams_config.json") -> dict:
    '''
    Load a mapping from external project IDs to quality model keys.
    '''
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    #  {'aws': ['AMEP11Beats', ...], ... }  →  {'AMEP11Beats':'aws', ...}
    return {team: qm.lower() for qm, teams in raw.items() for team in teams}


def choose_qualitymodel(external_id: str, explicit_qm: str | None, qm_map: dict) -> str:
    '''
    Decide which quality model to use for a project. Either the one specified in the event or the one from the config file.
    '''
    if explicit_qm:
        return explicit_qm.lower()
    return qm_map.get(external_id, "default")