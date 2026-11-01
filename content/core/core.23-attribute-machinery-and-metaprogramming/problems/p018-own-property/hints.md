## Hint 1

`property` keeps three functions and calls the right one: which descriptor method runs for
`c.x`, which for `c.x = v`, which for `del c.x`? What should happen when the function for that
operation is `None`? And why must `__set__` exist even when there is no setter?

## Hint 2

`@radius.setter` above `def radius(self, value)` means
`radius = radius.setter(<the new function>)`. The name `radius` is rebound to whatever
`.setter` returns.

```
__get__(instance, owner=None):
    if instance is None: return self
    if fget is None: raise AttributeError(f"property {name!r} of {type(instance).__name__!r} object has no getter")
    return fget(instance)

__set__(instance, value):  same shape with fset(instance, value)
__delete__(instance):      same shape with fdel(instance)

setter(fset):  return type(self)(self.fget, fset, self.fdel, self.__doc__)
```
