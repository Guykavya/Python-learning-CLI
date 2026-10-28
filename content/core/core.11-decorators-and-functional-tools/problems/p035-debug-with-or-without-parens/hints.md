## Hint 1

Write the normal decorator first, as an inner function `decorator(f)` that uses `prefix` and
`log` from the outer call. Then the only question is what `debug` returns at the end. What is
`func` in each of the three ways of calling `debug`?

## Hint 2

- `func is None`: the user wrote `debug()` or `debug(prefix=...)`. Return `decorator`.
- `func` is callable: the user wrote `@debug`. Return `decorator(func)`.
- otherwise: the user passed something else, such as a string. Raise `TypeError`.

## Hint 3

```
debug(func=None, *, prefix="DEBUG", log=None):
    record(line): print or log.append
    decorator(f):
        @wraps(f)
        wrapper(*args, **kwargs):
            call = f"{prefix}: {f.__name__}({arguments})"
            try: result = f(*args, **kwargs)
            except Exception as err: record(call + " raised " + name); raise
            record(f"{call} -> {result!r}")
            return result
        return wrapper
    if func is None: return decorator
    if not callable(func): raise TypeError(...)
    return decorator(func)
```
