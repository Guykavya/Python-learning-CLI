## Approach

A loop counts the attempts. A successful call ends everything with `return`. A matching
exception is caught: if it was the last attempt, a bare `raise` sends the same exception up
(with its original message and traceback). Otherwise we sleep and the loop goes round again.
An exception that does not match `exceptions` is never caught, so it leaves the function at once.

`except exceptions:` works both for one class and for a tuple of classes, because that is how
`except` itself works.

## Code

```python
import time
from functools import wraps


def retry(attempts, exceptions=(Exception,), delay=0.0, sleep=time.sleep):
    if attempts < 1:
        raise ValueError(f"attempts must be at least 1, got {attempts}")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts:
                        raise
                    sleep(delay)
        return wrapper
    return decorator
```

## Complexity

At most `attempts` calls of the function and `attempts - 1` sleeps. Extra memory is O(1).

## Another way

Keep the last error in a variable and raise it after the loop:

```python
last = None
for _ in range(attempts):
    try:
        return func(*args, **kwargs)
    except exceptions as err:
        last = err
        ...
raise last
```

This needs an extra check so that you do not sleep after the last attempt. The version with
`if attempt == attempts: raise` keeps the rule in one place.

The `sleep=` parameter is called **dependency injection**: the function receives the tool it
needs instead of reaching for a fixed one. It makes slow or random things (time, sleeping,
network) easy to replace in tests.
