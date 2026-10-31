## Approach

Three nested functions: `trace_calls(logger)` remembers the logger, `decorator(func)` remembers
the function, and `wrapper(*args, **kwargs)` runs on every call.

Inside `wrapper`:

1. If DEBUG is off, call `func` and return. No string is built, no `repr` runs.
2. Build the argument text and log the call.
3. Call `func` inside `try`. On an exception log it and re-raise with a bare `raise` (the
   original traceback stays intact). Otherwise log the result and return it.

Why the `isEnabledFor` check when logging is already lazy? Laziness only covers the work
**inside** `logger.debug`. `", ".join(repr(a) for a in args)` runs **before** `debug` is even
called, so we must skip it ourselves. (`result` and `exc` are passed as `%r` arguments, so for
those alone the laziness would have been enough.)

## Code

```python
import functools
import logging


def trace_calls(logger):
    def decorator(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not logger.isEnabledFor(logging.DEBUG):
                return func(*args, **kwargs)
            parts = [repr(a) for a in args]
            parts += [f"{key}={value!r}" for key, value in kwargs.items()]
            logger.debug("call %s(%s)", name, ", ".join(parts))
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                logger.debug("%s raised %r", name, exc)
                raise
            logger.debug("%s -> %r", name, result)
            return result

        return wrapper

    return decorator
```

## Complexity

O(size of the reprs) extra per call when DEBUG is on; one method call when it is off.

## Another way

`inspect.signature(func).bind(*args, **kwargs)` gives the arguments **with their parameter
names**, so the log could say `area(w=3, h=4, unit='cm')` even for positional calls. That is
nicer to read but slower, and the format here follows how the call was written.
