## Hint 1

`__getattr__` runs only when normal lookup fails. Which names will normal lookup find on the
proxy itself (think of `__init__`, `access_count`, the attributes you store)? Every other name
reaches `__getattr__`, where you can forward it with `getattr(target, name)`.

Your `__setattr__` refuses everything. So how does `__init__` store `_target`? Is there a way
to call the *original* attribute-setting code that `object` provides?

## Hint 2

```
__init__(target):
    object.__setattr__(self, "_target", target)
    object.__setattr__(self, "_counts", {})

__getattr__(name):
    target = object.__getattribute__(self, "_target")   # AttributeError if missing, never recursion
    value  = getattr(target, name)                       # raises before counting if missing
    counts = object.__getattribute__(self, "_counts")
    counts[name] = counts.get(name, 0) + 1
    return value

__setattr__ / __delattr__: raise AttributeError(f"cannot set {name!r}: read-only proxy")
```
