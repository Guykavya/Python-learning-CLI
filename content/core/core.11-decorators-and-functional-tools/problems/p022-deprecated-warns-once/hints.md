## Hint 1

You need a flag "has this function warned yet?". Each decorated function needs its **own**
flag. Which of the three layers runs **once per decorated function**: `deprecated`, `decorator`
or `wrapper`?

## Hint 2

Create `warned = False` inside `decorator`. Inside `wrapper` you change it, so you need
`nonlocal warned`. Check and set the flag before calling `func`.

## Hint 3

```
decorator(func):
    warned = False
    @wraps(func)
    wrapper(*args, **kwargs):
        nonlocal warned
        if not warned:
            warned = True
            text = f"{func.__name__} is deprecated: {message}"
            print(text) if log is None else log.append(text)
        return func(*args, **kwargs)
```
