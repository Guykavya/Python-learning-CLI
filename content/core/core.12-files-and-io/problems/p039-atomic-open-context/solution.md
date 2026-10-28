## Approach

`mkstemp` creates a unique empty file in the folder of `path` and returns an open low-level handle (`fd`) and the name.
`os.fdopen(fd, mode)` wraps it as a normal file. The inner `with` closes the file, which flushes the data, before
`os.replace` runs. If anything fails inside the outer `try`, the temp file is removed and the error is raised again.
The old `path` is only replaced in the last step, so it can never be half written.

## Code

```python
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def atomic_open(path, mode="w", **kwargs):
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, mode, **kwargs) as f:
            yield f
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
```

## Complexity

O(size written). The replace itself is O(1).

## Another way

Use a fixed temp name like `path.with_name(path.name + ".tmp")` and `open` it. It is simpler, but two writers at the
same time would use the same temp file. `mkstemp` gives a name that is unique.

Before the replace you can also call `f.flush()` and `os.fsync(f.fileno())` so the bytes are really on the disk.
