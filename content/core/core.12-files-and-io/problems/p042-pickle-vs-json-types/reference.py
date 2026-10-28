import json
import pickle


def save_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def json_loses(obj):
    try:
        back = json.loads(json.dumps(obj))
    except TypeError:
        return True
    return back != obj
