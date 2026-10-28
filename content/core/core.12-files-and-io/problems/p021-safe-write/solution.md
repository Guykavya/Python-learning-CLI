## Approach

Create the temp file in the **same folder** (`dir=`), because `os.replace` is only a single atomic step inside one file system. Write to it, and only then call `os.replace(tmp, path)`. Wrap everything in `try/except`: on any error, delete the temp file and re-raise with a bare `raise`. The old file was never opened for writing, so it stays intact.

## Code

```python
import os
import tempfile
from pathlib import Path


def safe_write(path, text):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
```

## Complexity

O(n) for writing the text.

## Another way

Use `tempfile.NamedTemporaryFile(dir=folder, delete=False)`. For stronger safety on power loss, call `f.flush()` and `os.fsync(f.fileno())` before the replace.
