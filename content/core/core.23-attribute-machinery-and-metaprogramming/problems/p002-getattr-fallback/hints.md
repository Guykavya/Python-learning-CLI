## Hint 1

If you store each value as a normal instance attribute in `__init__` (`setattr(self, name, value)`),
which names will ever reach `__getattr__`? Only the missing ones, so `__getattr__` only has to
think about defaults. Where do you keep the defaults so `__getattr__` can find them?
What should happen first in `__getattr__` when `name` starts with `"_"`?

## Hint 2

```
__init__(values, defaults):
    self._defaults = copy of defaults (or {})
    for each name, value in values: setattr(self, name, value)

__getattr__(name):
    if name starts with "_": raise AttributeError(... name ...)
    if name in self._defaults: return it
    raise AttributeError(... name ...)
```

Reading `self._defaults` is safe after the guard: if it were missing, the nested call for
`"_defaults"` stops at the guard instead of recursing.
