## Approach

The real file is only changed by the very last step, `os.replace`. Everything before it works on copies: the loaded
data in memory and the temp file on disk. So every earlier failure leaves the old file intact. The only thing to
clean up is the temp file, which exists only after we start writing it. Put the write and the replace inside one
`try` and delete the temp file in the `except`, then raise again.

## Code

```python
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
```

## Complexity

O(size of the data) time and memory.

## Another way

Reuse the `atomic_open` context manager from the earlier problem: `with atomic_open(path, "w") as f: json.dump(...)`.
Add `f.flush()` and `os.fsync(f.fileno())` before the replace if the data must survive a power cut.
