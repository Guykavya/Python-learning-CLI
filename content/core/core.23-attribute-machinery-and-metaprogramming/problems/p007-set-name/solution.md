## Approach

The descriptor holds configuration only: its `name` (learned in `__set_name__`) and its
`default`. The value lives in each instance's `__dict__` under that name. Because `Field` is a
data descriptor (it has `__set__` and `__delete__`), lookup asks it first, so the dict entry with
the same name never shadows it; `__get__` simply reads that entry.

## Code

```python
class Field:
    def __init__(self, default=None):
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        if self.name not in instance.__dict__:
            raise AttributeError(f"{self.name!r} has no value to delete")
        del instance.__dict__[self.name]
```

## Complexity

O(1) for every operation: one dict lookup or store.

## Another way

Many libraries store the value under a private name, `"_" + name`, and some keep a
`weakref.WeakKeyDictionary` on the descriptor that maps instance to value (useful when the
instance has no `__dict__`, for example with `__slots__`, and the instance is hashable).
Storing under the public name, as here, is the simplest choice for a data descriptor and keeps
`vars(obj)` readable.

Before `__set_name__` existed (Python 3.6) you had to repeat the name: `title = Field("title")`.
`__set_name__` removes that duplication and the typos it invites.
