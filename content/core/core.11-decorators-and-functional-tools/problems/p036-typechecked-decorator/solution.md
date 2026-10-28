## Approach

Hints come in three shapes, and `typing.get_origin` tells them apart:

| Hint | `get_origin` | Check |
|---|---|---|
| `int`, `type(None)` | `None` | `isinstance(value, hint)` |
| `list[int]` | `list` | `isinstance(value, list)` |
| `int \| None` | the union type | any member matches (recursive) |

The decorator reads the hints and the signature once. On every call it binds the arguments to
names, checks each one that has a hint, calls the function, and checks the result. Using
`bound.arguments` (without `apply_defaults`) means only the arguments the caller really passed
are checked.

## Code

```python
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
```

`type_name` uses `__name__` for classes (`int`) and falls back to `str(hint)` for things like
`int | None`, which have no simple name.

## Complexity

O(p) per call for p hinted parameters (a union adds a small loop over its members). The hints
and signature are read once at decoration time, not on every call.

## Another way

Checking the items of `list[int]` too (every item must be an `int`) is possible with
`get_args(hint)`, but it costs O(n) on every call for a list of n items. Real projects usually
check types **before** running, with a tool such as `mypy`, and use runtime checks only at
borders, for example on data that comes from a user or a file.
