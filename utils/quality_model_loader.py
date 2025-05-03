# utils/quality_model_loader.py
import os
from collections import defaultdict
  


def scan_quality_model_folder(root_dir, subfolder, props_loader, build_def):
    """
    - props_loader: función que lee el .properties → dict
    - build_def   : función que recibe (props, qm, filepath) → definition
    Devuelve   (ALL_BY_QM, EVENT_BY_QM)
    """
    all_by_qm, evt_by_qm = {}, {}

    for qm in os.listdir(root_dir):
        qm_path = os.path.join(root_dir, qm)
        if not os.path.isdir(qm_path):
            continue

        folder = os.path.join(qm_path, subfolder)      # p.ej.  QUALITY_MODELS/AWS/metrics
        if not os.path.isdir(folder):
            continue

        defs, evt_map = [], defaultdict(list)

        for dirpath, _, files in os.walk(folder):
            for fname in [f for f in files if f.endswith(".properties")]:
                fpath  = os.path.join(dirpath, fname)
                props  = props_loader(fpath)
                dfn    = build_def(props, qm.lower(), fpath)
                defs.append(dfn)

                for evt in props.get("relatedEvent", "").split(","):
                    evt = evt.strip()
                    if evt:
                        evt_map[evt].append(dfn)

        all_by_qm[qm.lower()] = defs
        evt_by_qm[qm.lower()] = dict(evt_map)

    return all_by_qm, evt_by_qm
