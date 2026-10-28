## Approach

`contextlib` turns common try/finally patterns into one-line `with` statements. `redirect_stdout` temporarily replaces `sys.stdout` and puts the old one back in its `__exit__`. `suppress` is a tiny manager whose `__exit__` returns `True` for the listed exception types.

The `return` inside a `with suppress(...)` block is a useful pattern: success returns early, failure falls through to the line after the block.

## Code

```python
import io
import os
from contextlib import redirect_stderr, redirect_stdout, suppress


def capture(func, *args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        result = func(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


def remove_if_exists(path):
    with suppress(FileNotFoundError):
        os.remove(path)
        return True
    return False


def to_int_or(text, default=None):
    with suppress(ValueError, TypeError):
        return int(text)
    return default
```

## Complexity

O(size of output) for `capture`; O(1) for the others.

## Another way

`try: ... except FileNotFoundError: return False` is the long form of `suppress`. Capturing output by hand with `sys.stdout = io.StringIO()` plus `finally` works but is easy to get wrong.
