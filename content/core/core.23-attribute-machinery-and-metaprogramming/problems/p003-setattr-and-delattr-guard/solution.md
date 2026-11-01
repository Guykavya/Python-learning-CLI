## Approach

Keep a `_locked` flag in each object's own `__dict__`. `__setattr__` refuses when the flag is
set, and otherwise stores the value the normal way with `object.__setattr__`. `__init__` uses
`object.__setattr__` for the fields (so it works the same whatever `__setattr__` does) and sets
the flag last. Because `object.__setattr__` skips the guard, `__init__` must check the flag
itself, or calling it again would quietly change a locked object.

## Code

```python
class Locked:
    def __init__(self, **fields):
        if self.__dict__.get("_locked", False):
            raise AttributeError(f"{type(self).__name__} is locked: cannot run __init__ again")
        for name, value in fields.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "_locked", True)

    def __setattr__(self, name, value):
        if self.__dict__.get("_locked", False):
            raise AttributeError(f"cannot set {name!r}: {type(self).__name__} is locked")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError(f"cannot delete {name!r}: {type(self).__name__} is locked")

    def __repr__(self):
        parts = [f"{k}={v!r}" for k, v in self.__dict__.items() if k != "_locked"]
        return f"{type(self).__name__}({', '.join(parts)})"
```

## Complexity

Each assignment does one extra dict lookup: O(1). `repr` is O(number of fields).

## Another way

`self.__dict__.update(fields)` and `self.__dict__["_locked"] = True` also bypass `__setattr__`,
because they change the dict directly instead of assigning an attribute. For real code,
`@dataclass(frozen=True)` gives you the same protection (it generates a `__setattr__` and
`__delattr__` that raise `FrozenInstanceError`, a subclass of `AttributeError`) plus `__eq__`
and `__repr__`. Write it by hand only to learn the hooks, or when you need a rule dataclasses
cannot express.
