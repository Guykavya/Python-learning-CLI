import json
import os
from pathlib import Path


def safe_update_json(path, fn):
    path = Path(path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    result = fn(data)
    if result is None:
        result = data

    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return result
