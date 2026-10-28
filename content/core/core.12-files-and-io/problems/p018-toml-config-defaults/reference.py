import copy
import tomllib

DEFAULTS = {"host": "localhost", "port": 8000, "debug": False, "tags": []}


def load_config(path):
    config = copy.deepcopy(DEFAULTS)
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return config
    config.update(data)
    return config
