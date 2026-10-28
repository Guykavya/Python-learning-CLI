## Hint 1

Read `@repeat(3)` as `f = repeat(3)(f)`. What must `repeat(3)` return so that putting `(f)` after it works?
And what must *that* return?

## Hint 2

Three nested functions. Check `n` in the outermost one, so a bad `n` fails before any function is decorated.

```
def repeat(n):
    if n < 1: raise ValueError(...)
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(n)]
        return wrapper
    return decorate
```
