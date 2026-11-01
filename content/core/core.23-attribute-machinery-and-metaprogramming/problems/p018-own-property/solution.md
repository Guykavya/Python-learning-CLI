## Approach

`Prop` is a data descriptor that holds three optional functions. Each descriptor method calls
the matching function or raises `AttributeError` when it is missing. Defining `__set__` and
`__delete__` unconditionally is the important part: it makes every `Prop` a data descriptor,
so it beats the instance dictionary and a read-only property really is read-only.

`getter`/`setter`/`deleter` copy the object with one function replaced. Returning a new object
(instead of changing `self`) keeps the original valid, which matters when a subclass extends
`Base.v`: `Base` must keep its read-only version. `__set_name__` gives the attribute name for
error messages.

## Code

```python
class Prop:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self.name = fget.__name__ if fget is not None else "?"

    def __set_name__(self, owner, name):
        self.name = name

    def _error(self, instance, missing):
        return AttributeError(
            f"property {self.name!r} of {type(instance).__name__!r} object has no {missing}"
        )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.fget is None:
            raise self._error(instance, "getter")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise self._error(instance, "setter")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise self._error(instance, "deleter")
        self.fdel(instance)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
```

## Complexity

Every access is O(1) plus the cost of the user's function. Compared with a plain attribute,
each access adds one or two Python function calls, which is why the C `property` exists.

## Another way

Copy the object and replace one field, instead of calling the constructor:

```python
import copy

def setter(self, fset):
    new = copy.copy(self)
    new.fset = fset
    return new
```

This also keeps the subclass type and any extra attributes a subclass added. The official
"Descriptor HowTo Guide" in the Python docs has a pure-Python `property` very close to the one
above; compare yours with it.
