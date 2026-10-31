## Hint 1

When you read `s.port`, Python looks in the object's own attributes first (`vars(s)`), then in its
class, then in the parent classes. So what must `__init__` store so that a missing override falls
through to the default? Only the overrides. How do you set an attribute whose name is in a variable?
(`setattr(obj, name, value)`, and `getattr` to read one.)

## Hint 2

`names()`: loop over `dir(cls)` and keep a name when it does not start with `"_"` and
`callable(getattr(cls, name))` is `False`. For `__init__`, the default to compare types with is
`getattr(type(self), name)`. `overrides()` is just a copy of `vars(self)`. `reset` can remove an
instance attribute with `delattr(self, name)`; the class attribute is untouched.

## Hint 3

```
__init__(self, **overrides):
    for name, value in overrides.items():
        if name not in self.names(): raise TypeError(f"unknown setting {name!r}")
        default = getattr(type(self), name)
        if type(value) is not type(default): raise TypeError(...)
        setattr(self, name, value)

as_dict():      {name: getattr(self, name) for name in self.names()}
reset(name):    check name; if name in vars(self): delattr(self, name)
with_changes(**changes):
    return type(self)(**{**self.overrides(), **changes})
```
