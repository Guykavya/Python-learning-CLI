## Hint 1

There are three layers: `retry(...)` takes the settings, `decorator(func)` takes the function,
and `wrapper(*args, **kwargs)` runs on every call. Where should the check `attempts < 1` go so
that it runs when `retry(0)` is called?

## Hint 2

Loop over the attempt numbers `1 .. attempts`. Inside, `try` the call and `return` at once if it
works. In the `except exceptions:` part, ask: "is this the last attempt?" If yes, re-raise.
If no, sleep.

## Hint 3

```
check attempts >= 1, else raise ValueError
decorator(func):
    @wraps(func)
    wrapper(*args, **kwargs):
        for attempt in 1 .. attempts:
            try: return func(*args, **kwargs)
            except exceptions:
                if attempt == attempts: raise
                sleep(delay)
```
