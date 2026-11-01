## Approach

Do by hand what attribute lookup does automatically: ask the function's `__get__` for a bound
method. A bound method is immutable, so `rebind` takes the underlying function out of it
(`__func__`) and binds that to the new object.

## Code

```python
def bind(func, obj):
    return func.__get__(obj, type(obj))


def method_parts(method):
    return method.__func__, method.__self__


def rebind(method, other):
    return method.__func__.__get__(other, type(other))
```

## Complexity

O(1): each call creates one small method object.

## Another way

`types.MethodType` is the class of bound methods; calling it builds one:

```python
from types import MethodType

def bind(func, obj):
    return MethodType(func, obj)
```

This is also why `acc.deposit is acc.deposit` is `False`: every attribute read calls `__get__`
again and creates a fresh bound method (they compare equal with `==`, because both hold the
same function and the same instance).
