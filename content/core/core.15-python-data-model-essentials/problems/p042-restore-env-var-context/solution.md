## Approach

This is the most common use of `@contextmanager`: **save, change, `yield`, restore in `finally`**. The generator form is shorter than a class with `__enter__`/`__exit__`, and the local variable `saved` is the state that a class would keep in `self`.

Using `None` as the marker for "was not set" works because real environment values are always strings. Placing the change loop inside `try` and the restore in `finally` makes the manager safe against failures in the set-up itself.

## Code

```python
import os
from contextlib import contextmanager


@contextmanager
def temp_env(**changes):
    saved = {name: os.environ.get(name) for name in changes}
    try:
        for name, value in changes.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = str(value)
        yield os.environ
    finally:
        for name, old in saved.items():
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
```

## Complexity

O(k) for k variables.

## Another way

`unittest.mock.patch.dict(os.environ, {...})` does exactly this in the standard library; pytest's `monkeypatch.setenv` is the same idea for test functions. A class with `__enter__`/`__exit__` is also fine and easier to reuse as an object.
