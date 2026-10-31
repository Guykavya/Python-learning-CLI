## Approach

The flag must live in the closure of `decorator`, because `decorator` runs once for each
function you decorate. Then every decorated function gets a fresh `warned = False`. The
`wrapper` changes the flag, so it needs `nonlocal`.

The warning is recorded before `func(...)` is called, so a call that raises still counts as the
first call.

## Code

```python
from functools import wraps


def deprecated(message, log=None):
    def decorator(func):
        warned = False

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal warned
            if not warned:
                warned = True
                text = f"{func.__name__} is deprecated: {message}"
                if log is None:
                    print(text)
                else:
                    log.append(text)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Complexity

O(1) extra work per call.

## Another way

Store the flag on the wrapper as an attribute: `wrapper.warned = False` after defining it, and
`if not wrapper.warned: wrapper.warned = True` inside. No `nonlocal` is needed, and a test can
read or reset the flag from outside.

Real Python code uses the `warnings` module (`warnings.warn(text, DeprecationWarning)`), which
also shows each warning only once per place by default. Here we use a list so you can see and
test the "once" rule yourself.
