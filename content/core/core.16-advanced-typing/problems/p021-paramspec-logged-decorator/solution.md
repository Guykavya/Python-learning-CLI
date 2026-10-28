## Approach

`Callable[P, R]` says "a function whose parameters are `P` and whose result is `R`". If the
decorator takes `Callable[P, R]` and returns `Callable[P, R]`, the type checker knows the decorated
function has exactly the same parameters and result as before. Inside, `*args: P.args` and
`**kwargs: P.kwargs` are the only way to say "pass on whatever `P` is". `functools.wraps` copies
the name and docstring and sets `__wrapped__`, which `inspect.signature` follows, so the run-time
signature is also correct.

`logged_as` is a factory: calling it with the prefix returns the real decorator, so there are
three levels: `logged_as(prefix)` -> `decorator(func)` -> `wrapper(*args, **kwargs)`.

## Code

```python
import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

CALL_LOG: list[str] = []


def _describe(name: str, args: tuple[object, ...], kwargs: dict[str, object]) -> str:
    parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{name}({', '.join(parts)})"


def logged(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        CALL_LOG.append(_describe(func.__name__, args, kwargs))
        return func(*args, **kwargs)

    return wrapper


def logged_as(prefix: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            CALL_LOG.append(f"{prefix}: {_describe(func.__name__, args, kwargs)}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
```

## Complexity

O(k) extra work per call for building the log line, where k is the number of arguments.

## Another way

`logged_as` could call `logged` and then prepend the prefix, or both could share one inner
function that takes the prefix. In Python 3.12+ you can drop the `TypeVar` lines and write
`def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:`.
