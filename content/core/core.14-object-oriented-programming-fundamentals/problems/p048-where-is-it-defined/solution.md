## Approach

This is exactly what Python does on every attribute lookup through a class (chapter section 9):
walk `cls.__mro__` from left to right and stop at the first class whose own namespace contains the
name. `vars(klass)` is that namespace (a read-only view of `klass.__dict__`). `name in vars(klass)`
is `True` only for names the class defines itself, not for inherited ones.

`all_definitions` keeps walking instead of stopping, so you see the whole chain of overrides.

## Code

```python
def defined_in(cls, name):
    if not isinstance(cls, type):
        raise TypeError("defined_in() needs a class")
    for klass in cls.__mro__:
        if name in vars(klass):
            return klass
    return None


def all_definitions(cls, name):
    if not isinstance(cls, type):
        raise TypeError("all_definitions() needs a class")
    return [klass.__name__ for klass in cls.__mro__ if name in vars(klass)]
```

## Complexity

O(m) for an MRO of m classes: each `in vars(klass)` is a dict lookup.

## Another way

You could write it with `next()` and a generator expression:
`return next((k for k in cls.__mro__ if name in vars(k)), None)`. To ask the question about an
**object**, first check `name in vars(obj)` (the instance wins for normal attributes), then call
`defined_in(type(obj), name)`. Properties are the exception: they live on the class and still beat the
instance dict (chapter section 9).
