## Approach

Make a deep copy of `DEFAULTS` first, so the nested `tags` list is not shared. Open the file in **binary** mode (`"rb"`), because `tomllib` decodes UTF-8 itself. Call `tomllib.load(f)`, then `config.update(data)` so the file wins. Catch only `FileNotFoundError`, so bad TOML still raises.

## Code

```python
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
```

## Complexity

O(n) in the size of the file.

## Another way

`{**DEFAULTS, **data}` also merges, but it makes a shallow copy: the default `tags` list would be shared. Use `copy.deepcopy` on the defaults or build `"tags": []` fresh inside the function.
