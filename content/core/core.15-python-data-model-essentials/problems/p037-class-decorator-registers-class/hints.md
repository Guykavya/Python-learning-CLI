## Hint 1

`@reg` means `Dog = reg(Dog)`. `@reg(name="x")` means `Dog = reg(name="x")(Dog)`. In the first case `__call__` gets the class as its first argument; in the second it gets nothing but `name`. What default value for the first parameter lets one method tell the two cases apart? What must it return in each case?

## Hint 2

Signature: `def __call__(self, cls=None, *, name=None)`. Define an inner function `decorate(klass)` that does the registering and returns `klass`. Then: `if cls is None: return decorate` (the `@reg(name=...)` form: Python will call the result with the class), else `return decorate(cls)` (the plain form).

## Hint 3

```
__call__(cls=None, *, name=None):
    def decorate(klass):
        key = name or klass.__name__.lower(); ValueError if key in store
        store[key] = klass; klass.registered_name = key; return klass
    return decorate if cls is None else decorate(cls)
auto_repr(cls):
    def __repr__(self): ... uses cls._fields, type(self).__name__, getattr
    cls.__repr__ = __repr__ ; return cls
```
