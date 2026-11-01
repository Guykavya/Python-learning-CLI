## Approach

Both decorators are non-data descriptors that wrap a function. The difference is only in what
`__get__` hands back. `ClassMethod` ignores the instance and binds the function to the owner
class with `types.MethodType`, so the call receives the class first. Because the owner is the
class the lookup started from, subclasses automatically get themselves. `StaticMethod`
returns the raw function, so nothing is bound and nothing extra is passed.

## Code

```python
from types import MethodType


class ClassMethod:
    def __init__(self, func):
        self.__func__ = func
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)
        return MethodType(self.__func__, owner)


class StaticMethod:
    def __init__(self, func):
        self.__func__ = func
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner=None):
        return self.__func__

    def __call__(self, *args, **kwargs):
        return self.__func__(*args, **kwargs)
```

## Complexity

O(1) per access. `ClassMethod` creates a new bound-method object on every access (as normal
methods do), which is why `Temperature.from_fahrenheit is Temperature.from_fahrenheit` is
`False` while `Temperature.c_to_f is Temperature.c_to_f` is `True`.

## Another way

Functions are descriptors themselves, so you can ask the function to bind itself:

```python
def __get__(self, instance, owner=None):
    if owner is None:
        owner = type(instance)
    return self.__func__.__get__(owner, type(owner))
```

`func.__get__(obj, type)` returns `MethodType(func, obj)`. Here `obj` is the class, so the
result is a method bound to the class. This is the same mechanism that turns `obj.method`
into a bound method, used one level up.
