## Hint 1

Build the text `name(arguments)` before you call the function. Then you can use it for both endings: the
normal one and the error one. How do you get `'Ann'` with quotes from the string `Ann`?

## Hint 2

Put the call in `try`. In `except Exception as error`, log `type(error).__name__` and use a bare `raise` so
the caller still gets the error. Log the success line only after the call returned.

## Hint 3

```
parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
call = f"{func.__name__}({', '.join(parts)})"
try: result = func(*args, **kwargs)
except Exception as error:
    log.append(f"{call} raised {type(error).__name__}"); raise
log.append(f"{call} -> {result!r}")
return result
```
