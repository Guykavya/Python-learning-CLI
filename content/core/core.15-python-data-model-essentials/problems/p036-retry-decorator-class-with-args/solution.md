## Approach

A decorator with arguments is a **factory**: `Retry(times=3)` is evaluated first and must return something callable that accepts the function. A class does this naturally: `__init__` stores the configuration, `__call__(func)` returns the wrapper. The wrapper is an ordinary closure over `func` and `self`.

The attempt loop returns on the first success. In `except self.exceptions` (a tuple works there), failures are counted, and on the last attempt a bare `raise` re-raises the exception being handled. Exceptions outside the tuple are not caught at all, so they leave the loop immediately.

## Code

```python
import functools


class Retry:
    def __init__(self, times=3, exceptions=(Exception,)):
        if times < 1:
            raise ValueError("times must be at least 1")
        self.times = times
        self.exceptions = exceptions
        self.failures = 0

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, self.times + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions:
                    self.failures += 1
                    if attempt == self.times:
                        raise
        return wrapper
```

## Complexity

At most `times` calls of `func`; O(1) extra memory.

## Another way

Three nested functions: `def retry(times, exceptions): def decorator(func): def wrapper(...)`. It does the same, but the failure counter would need `nonlocal` or an attribute on the wrapper, and there is no place for methods like `reset()`.
