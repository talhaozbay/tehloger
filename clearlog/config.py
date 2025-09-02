# clearlog/config.py
import yaml, os
DEFAULT = {"threshold":{"window_sec":300,"max_fails":3}, "max_events":500}
def load(path="configs/default.yaml"):
    if os.path.exists(path):
        with open(path,"r") as f: return {**DEFAULT, **yaml.safe_load(f)}
    return DEFAULT
