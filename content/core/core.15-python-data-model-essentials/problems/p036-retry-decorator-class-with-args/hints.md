## Hint 1

The line `@Retry(times=3)` runs `Retry(times=3)` **first**. What does the result then have to be able to do so that Python can apply it to the function below? Which special method?

## Hint 2

`except self.exceptions:` accepts a tuple of classes. A loop `for attempt in range(1, self.times + 1)` with `return func(...)` inside the `try` ends the function on success. In the `except`, count the failure; if `attempt == self.times` use a bare `raise` to re-raise the last exception.

## Hint 3

```
__init__(times, exceptions): validate times >= 1; store times, exceptions; failures = 0
__call__(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in 1..times:
            try: return func(*args, **kwargs)
            except self.exceptions: failures += 1 ; if attempt == times: raise
    return wrapper
```
