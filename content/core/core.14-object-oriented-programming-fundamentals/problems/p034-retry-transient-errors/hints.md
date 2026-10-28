## Hint 1

Which exceptions should the loop catch? If you write `except Exception`, what happens to a
`PermanentError` or a `KeyError`? Catching only `TransientError` lets everything else fly past the
loop unchanged, which is exactly what we want.

## Hint 2

Loop with an attempt number: `for number in range(1, attempts + 1)`. Inside, `return func()`
ends everything on success. In the `except` block, how do you know this was the last attempt?
Then `raise RetryExhausted(attempts, err) from err` sets `__cause__`.

## Hint 3

```
retry(func, attempts, on_retry):
    if attempts is not an int or attempts < 1: raise ValueError
    for number in 1..attempts:
        try:
            return func()
        except TransientError as err:
            if number == attempts:
                raise RetryExhausted(attempts, err) from err
            if on_retry is not None: on_retry(number, err)

retrying(attempts):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry(lambda: func(*args, **kwargs), attempts)
        return wrapper
    return decorator
```
