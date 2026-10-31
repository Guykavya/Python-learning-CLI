## Approach

Write a helper `convert(obj)` and pass it as `default=convert`. JSON calls it only for objects it cannot handle itself. Return a simple value for the types you know. For everything else, **raise `TypeError`**, so mistakes are not hidden. `datetime` is a subclass of `date`, so one `isinstance` check covers both.

## Code

```python
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
```

## Complexity

O(n log n) at worst, because sets are sorted.

## Another way

Convert the data before dumping with a recursive function. That is longer. `default=` is shorter because JSON walks the nested data for you.
