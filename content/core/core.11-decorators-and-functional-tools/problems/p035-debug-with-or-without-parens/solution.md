## Approach

Build the decorator once, as an inner function that reads `prefix` and `log` from the
enclosing call. Then decide how `debug` was used by looking at `func`:

- `@debug` means Python calls `debug(add)`. `func` is the function, and the options keep their
  defaults. We decorate at once and return the wrapper.
- `@debug(...)` means Python calls `debug(prefix=..., log=...)` with no function. `func` is `None`,
  so we return the decorator, and Python calls it with the function next.

Making `prefix` and `log` keyword-only (after `*`) is what makes this safe: the **only**
positional argument can be the function. A string passed by position is a user mistake, and we
say so clearly instead of failing later with a strange error.

## Code

```python
from functools import wraps


def debug(func=None, *, prefix="DEBUG", log=None):
    def record(line):
        if log is None:
            print(line)
        else:
            log.append(line)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            parts = [repr(a) for a in args]
            parts += [f"{k}={v!r}" for k, v in kwargs.items()]
            call = f"{prefix}: {f.__name__}({', '.join(parts)})"
            try:
                result = f(*args, **kwargs)
            except Exception as err:
                record(f"{call} raised {type(err).__name__}")
                raise
            record(f"{call} -> {result!r}")
            return result
        return wrapper

    if func is None:
        return decorator
    if not callable(func):
        raise TypeError(
            f"debug() got {func!r} instead of a function. "
            f'To set the prefix, write @debug(prefix="{func}").'
        )
    return decorator(func)
```

## Complexity

O(1) extra per call plus the `repr` of the arguments and result.

## Another way

`functools.partial` gives a short form of the same idea:

```python
def debug(func=None, *, prefix="DEBUG", log=None):
    if func is None:
        return partial(debug, prefix=prefix, log=log)
    ...  # decorate func directly
```

`debug(prefix="X")` returns `partial(debug, prefix="X", log=None)`. When Python calls that
partial with the function, it runs `debug(func, prefix="X", log=None)`, which now has a function.
The decorator code lives in one place and there is no separate inner `decorator`.
