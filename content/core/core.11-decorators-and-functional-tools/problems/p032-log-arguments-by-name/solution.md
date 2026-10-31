## Approach

The signature never changes, so compute it once when decorating. On each call, `bind` does the
same matching Python does when it calls a function: positional arguments fill parameters in
order, keywords fill them by name, extra positionals go into `*args`. If the call does not fit,
`bind` raises the same kind of `TypeError` that the real call would raise, so we fail before
logging.

Why does it work on top of `shout`? `shout` used `wraps`, so its wrapper has `__wrapped__`
pointing at the real `greet`. `inspect.signature` follows `__wrapped__` and reports
`(name, punct='!')` instead of `(*args, **kwargs)`. This is the hidden reason every decorator
should use `wraps`: tools that inspect functions (help(), documentation tools, test frameworks,
and this decorator) keep working.

## Code

```python
import inspect
from functools import wraps


def log_arguments(log):
    def decorator(func):
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            parts = [f"{name}={value!r}" for name, value in bound.arguments.items()]
            log.append(f"{func.__name__}({', '.join(parts)})")
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Complexity

O(p) per call for p parameters, plus the `repr` of each value.

## Another way

You could call `func(*bound.args, **bound.kwargs)` instead of `func(*args, **kwargs)`. After
`apply_defaults()` this passes the defaults explicitly, which gives the same result for normal
functions. Passing the original `args` and `kwargs` through is simpler and changes nothing about
the call, which is what a logging decorator should promise.
