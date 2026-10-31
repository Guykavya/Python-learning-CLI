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
