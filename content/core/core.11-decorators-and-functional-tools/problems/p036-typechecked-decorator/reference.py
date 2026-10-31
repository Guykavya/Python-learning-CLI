import inspect
import typing
from functools import wraps

UNION_ORIGINS = (typing.Union, type(int | str))


def type_name(hint):
    return getattr(hint, "__name__", str(hint))


def matches(value, hint):
    origin = typing.get_origin(hint)
    if origin is None:
        return isinstance(value, hint)
    if origin in UNION_ORIGINS:
        return any(matches(value, member) for member in typing.get_args(hint))
    return isinstance(value, origin)


def typechecked(func):
    hints = typing.get_type_hints(func)
    sig = inspect.signature(func)
    name = func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for param, value in bound.arguments.items():
            if param in hints and not matches(value, hints[param]):
                raise TypeError(
                    f"{name}: argument '{param}' must be {type_name(hints[param])}, "
                    f"got {type(value).__name__}"
                )
        result = func(*args, **kwargs)
        if "return" in hints and not matches(result, hints["return"]):
            raise TypeError(
                f"{name}: return value must be {type_name(hints['return'])}, "
                f"got {type(result).__name__}"
            )
        return result
    return wrapper
