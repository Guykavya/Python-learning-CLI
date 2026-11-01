## Approach

The proxy keeps two private attributes in its own `__dict__`: the target and a dict of
counts. Normal lookup finds those, the methods defined in the class, and nothing else. Every
other name falls through to `__getattr__`, which forwards to the target and counts the read
after it succeeded. `__setattr__` and `__delattr__` refuse everything, so `__init__` must
bypass them with `object.__setattr__`.

Inside `__getattr__`, `self._target` is dangerous: if `_target` is missing (a proxy built by
`copy` or `pickle` without `__init__`), that very read calls `__getattr__("_target")` again,
forever. `object.__getattribute__(self, "_target")` is the normal lookup without the
fallback, so a missing name is a plain `AttributeError`, which `hasattr` and `copy` expect.

## Code

```python
class ReadOnlyProxy:
    def __init__(self, target):
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_counts", {})

    def __getattr__(self, name):
        target = object.__getattribute__(self, "_target")
        value = getattr(target, name)
        counts = object.__getattribute__(self, "_counts")
        counts[name] = counts.get(name, 0) + 1
        return value

    def __setattr__(self, name, value):
        raise AttributeError(f"cannot set {name!r}: read-only proxy")

    def __delattr__(self, name):
        raise AttributeError(f"cannot delete {name!r}: read-only proxy")

    def access_count(self, name):
        return self._counts.get(name, 0)

    def __repr__(self):
        return f"ReadOnlyProxy({self._target!r})"
```

`access_count` and `__repr__` can use `self._target` safely: they run only on a proxy whose
`__init__` ran, and even if not, a missing `_target` there goes to `__getattr__`, which now
ends in `AttributeError` instead of recursion.

## Complexity

Each forwarded read is O(1) plus the target's own lookup.

## Another way

Refuse private names in `__getattr__` before touching your own state. It is simpler, but the
target's own `_private` attributes are then hidden too:

```python
def __getattr__(self, name):
    if name.startswith("_"):
        raise AttributeError(name)
    value = getattr(self._target, name)
    self._counts[name] = self._counts.get(name, 0) + 1
    return value
```

Note the limit of any read-only proxy: methods run on the real target, so
`proxy.items.append(3)` or a method like `order.pay()` can still change it. A proxy controls
attribute access, not what the target's own code does. For real immutability, give out a
copy or a frozen dataclass.
