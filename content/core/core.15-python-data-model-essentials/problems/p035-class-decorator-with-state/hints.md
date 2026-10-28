## Hint 1

A class used as a decorator is called with the function (`Recorder(func)` runs `__init__`) and the resulting object is called later (`__call__`). Where should the list `calls` be created so that each decorated function gets its own? What lets `__name__` and `__doc__` be copied from `func` to the object?

## Hint 2

In `__call__`, wrap the call in `try`/`except Exception as err`: on success append `(args, kwargs, "ok", result)` and return the result; on failure append `(args, kwargs, "error", err)` and `raise` (a bare `raise` re-raises the same exception). For `last_result`, walk `self.calls` from the end and return the first entry whose status is `"ok"`.

## Hint 3

```
__init__: functools.update_wrapper(self, func); self.func = func; self.calls = []
__call__(*a, **kw):
    try: result = func(*a, **kw)
    except Exception as err: record error; raise
    record ok; return result
@property last_result: for entry in reversed(calls): if ok -> return value ; raise LookupError
```
