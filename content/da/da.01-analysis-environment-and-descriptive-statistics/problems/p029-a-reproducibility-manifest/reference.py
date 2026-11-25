import copy
import hashlib
import json
import platform


def manifest(values, seed, params):
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {
        "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "seed": seed,
        "params": copy.deepcopy(params),
        "python": platform.python_version(),
        "n": len(values),
    }
