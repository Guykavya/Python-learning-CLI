## Approach

Save the old folder first, change folder, then `yield` inside `try`, and restore in `finally`. The `chdir` that can
fail is **before** the `try`, so if it fails nothing has changed and nothing needs to be restored.

## Code

```python
import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def working_dir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield Path.cwd()
    finally:
        os.chdir(old)
```

## Complexity

O(1).

## Another way

In Python 3.11 and later, `contextlib.chdir(path)` does the same. Writing it yourself shows what a context manager
is made of: set up, `yield`, clean up in `finally`.
