## Approach

Store the given values as ordinary instance attributes. The normal lookup then finds them
without calling any hook, and only names that are **not** stored reach `__getattr__`. There we
check the defaults and otherwise raise `AttributeError`.

The underscore guard comes first, before `self` is touched. On an object made by `copy` or
`pickle`, `__init__` has not run, so `self._defaults` does not exist; without the guard, reading
it calls `__getattr__("_defaults")`, which reads it again, forever.

## Code

```python
class Settings:
    def __init__(self, values, defaults=None):
        self._defaults = dict(defaults or {})
        for name, value in values.items():
            setattr(self, name, value)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        defaults = self._defaults
        if name in defaults:
            return defaults[name]
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
```

## Complexity

A stored name: one normal lookup, no hook. A default: one failed lookup plus one dict lookup.
All O(1).

## Another way

Keep everything in a `collections.ChainMap(values, defaults)` and forward all public names to
it, turning `KeyError` into `AttributeError`:

```python
def __getattr__(self, name):
    chain = self.__dict__.get("_chain")        # no recursion: __dict__ always exists
    if chain is None or name.startswith("_"):
        raise AttributeError(name)
    try:
        return chain[name]
    except KeyError:
        raise AttributeError(f"no setting {name!r}") from None
```

With this design assignments must also go into the chain (a small `__setattr__`), so the first
version is simpler.
