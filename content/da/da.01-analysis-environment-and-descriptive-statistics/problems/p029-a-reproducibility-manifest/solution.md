## Approach

A hash is a fingerprint of bytes, so first turn the data into one canonical byte string: sorted keys, no optional spaces, UTF-8. Then the same data always gives the same digest, and a single changed digit changes it completely. Copying `params` protects the record from later edits by the caller. The Python version is part of the record because a result may depend on it.

## Code

```python
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

```

## Complexity

O(size of the data) for the JSON text and the hash.

## Another way

Hash the original file bytes instead (`hashlib.sha256(path.read_bytes())`), which also catches changes you cannot see after parsing. Tools such as DVC and Git do this for whole files.
