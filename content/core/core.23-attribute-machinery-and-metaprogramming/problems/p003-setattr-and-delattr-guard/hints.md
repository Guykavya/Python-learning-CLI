## Hint 1

You need a flag that says "this object is locked". Where must it live so each object has its
own? How does `__setattr__` read it without causing trouble on a brand-new object that does not
have the flag yet? (`self.__dict__.get(...)` never calls your hooks.) And how does `__init__`
store values once your own `__setattr__` is in the way?

## Hint 2

```
__init__(**fields):
    if this object's dict says locked: raise AttributeError
    for name, value in fields: object.__setattr__(self, name, value)
    object.__setattr__(self, "_locked", True)

__setattr__(name, value):
    if self.__dict__.get("_locked"): raise AttributeError(mention name)
    object.__setattr__(self, name, value)

__delattr__(name): raise AttributeError(mention name)

__repr__: join "k=repr(v)" for k, v in self.__dict__.items() if k != "_locked"
```
