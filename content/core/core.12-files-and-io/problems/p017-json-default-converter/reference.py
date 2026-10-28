import json
from datetime import date, datetime
from pathlib import Path


def convert(obj):
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def dump_json(data):
    return json.dumps(data, sort_keys=True, default=convert)
