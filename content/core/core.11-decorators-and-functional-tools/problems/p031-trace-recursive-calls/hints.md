## Hint 1

The depth is state that must survive between calls and belong to one decorated function. Where
do you create it, and which keyword lets `wrapper` change it? When do you add 1, and when do you
take 1 away again?

## Hint 2

Compute the indent **before** you increase the depth, and use that same indent for the `->` line.
Put the call inside `try` / `except` / `finally`: `except` logs `!!` and re-raises, `finally`
lowers the depth no matter what happened.

## Hint 3

```
decorator(func):
    depth = 0
    @wraps(func)
    wrapper(*args, **kwargs):
        nonlocal depth
        indent = "  " * depth
        log name(arguments) with indent
        depth += 1
        try: result = func(*args, **kwargs)
        except Exception as err: log indent + "!! " + type(err).__name__; raise
        finally: depth -= 1
        log indent + "-> " + repr(result)
        return result
```
