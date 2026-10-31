## Hint 1

The clock is just a function you were given. Where do you call it so that the duration covers only the
original call? And how can code run "after the call" even when the call raises?

## Hint 2

`try: return func(...)` together with `finally: ...` runs the `finally` part on both a normal return and an
error, and the return value or the error still goes to the caller.

## Hint 3

```
def decorate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = clock()
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.durations.append(clock() - start)
    wrapper.durations = []
    return wrapper
```
