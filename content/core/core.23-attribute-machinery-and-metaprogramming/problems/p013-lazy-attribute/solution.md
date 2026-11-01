## Approach

Lean on the lookup order instead of fighting it. `lazy` is a non-data descriptor, so it is
consulted only when the instance `__dict__` has no entry with that name. The first read
computes the value and writes it into the instance dict; from then on the plain dictionary
lookup answers and the descriptor is never involved. Deleting the entry makes the descriptor
visible again, so the next read recomputes.

`__set_name__` gives the real attribute name, which matters when the descriptor is created
from a function with a different name (`total = lazy(_compute_total)`).

## Code

```python
class lazy:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.name] = value
        return value
```

`self.name = func.__name__` in `__init__` is only a fallback for a `lazy` created outside a
class body (then `__set_name__` is never called).

## Complexity

The first read costs whatever `func` costs; every later read is one dictionary lookup, O(1),
with no Python-level function call at all.

## Another way

Because `lazy` has no `__set__`, plain `setattr(instance, self.name, value)` also lands in the
instance dict, and `functools.update_wrapper(self, func)` copies `__doc__`, `__name__` and
friends in one call:

```python
import functools

class lazy:
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        value = self.func(instance)
        setattr(instance, self.name, value)
        return value
```

In real code use `functools.cached_property`; it is this same idea. Like `lazy`, it needs an
instance `__dict__`, so it does not work on classes with `__slots__` (no dict to cache into).
