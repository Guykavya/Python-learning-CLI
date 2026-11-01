## Approach

One `Typed` object lives in the class and serves every instance, so it must never keep a value
on `self`. It keeps only configuration (the types, its name) and stores values in each
instance's `__dict__` under the field name. That works even though the key equals the
attribute name, because a data descriptor (it has `__set__`) wins over the instance dictionary
in the lookup order: `p.x` always goes through `__get__`.

Order matters in the check: test for `bool` first, since `isinstance(True, int)` is true.

## Code

```python
class Typed:
    def __init__(self, *types, allow_bool=False):
        if not types:
            raise TypeError("Typed needs at least one type")
        for t in types:
            if not isinstance(t, type):
                raise TypeError(f"Typed expects classes, got {t!r}")
        self.types = types
        self.allow_bool = allow_bool or bool in types
        self.name = None
        self.owner_name = None

    def __set_name__(self, owner, name):
        self.owner_name = owner.__name__
        self.name = name

    def _label(self):
        return f"{self.owner_name}.{self.name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self._label()} has not been set") from None

    def __set__(self, instance, value):
        if isinstance(value, bool) and not self.allow_bool:
            ok = False
        else:
            ok = isinstance(value, self.types)
        if not ok:
            expected = " or ".join(t.__name__ for t in self.types)
            raise TypeError(f"{self._label()} must be {expected}, got {type(value).__name__}")
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        try:
            del instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self._label()} has not been set") from None
```

`from None` hides the internal `KeyError` from the traceback: the user only needs to know the
field is unset.

## Complexity

O(k) per assignment for k allowed types (`isinstance` with a tuple), O(1) per read.

## Another way

Store under a private key such as `"_x"` and read it with `getattr(instance, key, MISSING)`:

```python
MISSING = object()

def __set_name__(self, owner, name):
    self.owner_name, self.name, self.key = owner.__name__, name, "_" + name

def __get__(self, instance, owner=None):
    if instance is None:
        return self
    value = getattr(instance, self.key, MISSING)
    if value is MISSING:
        raise AttributeError(f"{self.owner_name}.{self.name} has not been set")
    return value
```

Both work. The private key shows up in `vars(p)` as `_x`, which some people find clearer,
others find noisy. For checking many fields of a plain record, a dataclass plus a type checker
(mypy) catches most of these mistakes before the program even runs; descriptors are for when
you need the check at run time.
