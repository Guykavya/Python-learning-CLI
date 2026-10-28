## Hint 1

You can call `inspect.signature(func)` once, at decoration time, and keep the result in the
closure. Inside `wrapper`, what two method calls turn `(*args, **kwargs)` into a complete dict of
parameter names and values?

## Hint 2

`bound.arguments` is a dict in signature order. Build `name=repr(value)` for each pair with an
f-string and `!r`, join with `", "`. Bind **before** you log and before you call, so a bad call
fails early.

## Hint 3

```
decorator(func):
    sig = inspect.signature(func)
    @wraps(func)
    wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        parts = [f"{name}={value!r}" for name, value in bound.arguments.items()]
        log.append(f"{func.__name__}({', '.join(parts)})")
        return func(*args, **kwargs)
```
