## Hint 1

What does the wrapper receive? How can it pass on *any* arguments without knowing them? And which two type variables describe "the parameters of `func`" and "what `func` returns"?

## Hint 2

`P = ParamSpec("P")` stands for the whole parameter list, `R = TypeVar("R")` for the result. The wrapper is `def wrapper(*args: P.args, **kwargs: P.kwargs) -> R`. Decorate it with `@functools.wraps(func)`. A factory is a function that returns a decorator, so it needs one more level of `def`.

## Hint 3

```
def logged(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        CALL_LOG.append(name(parts))
        return func(*args, **kwargs)
    return wrapper

def logged_as(prefix):
    def decorator(func): ... same wrapper, with prefix + ": " ...
    return decorator
```
Write the string builder once as a helper and use it in both.
