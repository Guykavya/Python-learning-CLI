## Hint 1

The shape is a decorator **factory**: `trace_calls(logger)` returns `decorator`,
`decorator(func)` returns `wrapper`, and `wrapper(*args, **kwargs)` does the work. Where does
`@functools.wraps(func)` go? How do you build `"3, 4, unit='cm'"` from `args` and `kwargs`?

## Hint 2

Check `logger.isEnabledFor(logging.DEBUG)` at the start of `wrapper`, every call (the level
can change while the program runs). For the exception case use `except Exception as exc:`, log,
then a bare `raise` so the original traceback is kept.

```
wrapper(*args, **kwargs):
    if not logger.isEnabledFor(DEBUG): return func(*args, **kwargs)
    parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
    logger.debug("call %s(%s)", func.__name__, ", ".join(parts))
    try: result = func(*args, **kwargs)
    except Exception as exc: logger.debug("%s raised %r", name, exc); raise
    logger.debug("%s -> %r", name, result)
    return result
```
