## Hint 1

`Box[int]` is just a call: `Box.__class_getitem__(int)` (it is automatically a classmethod, so
`cls` is the class being subscripted). Whatever it returns is the value of `Box[int]`. To return
a *new class*, use `type(name, bases, namespace)` from the chapter: which base, which name, and
which class attributes does the new class need so that the inherited `put` checks the right type?

Then: what does `__class_getitem__` receive for `Box[int, str]`? Print it to see. And where can
you keep already-made classes so the second `Box[int]` returns the first one? What goes into the
key so that `Special[int]` and `Box[int]` do not collide?

## Hint 2

```
_EMPTY = object()            # "no value yet" (None is a valid value)

class Box:
    item_type = object       # what users see
    _check_type = object     # what isinstance uses
    _parameterised = False
    _cache = {}

    put(value):  if not isinstance(value, self._check_type): raise TypeError(...)
    get():       if self._value is _EMPTY: raise LookupError("box is empty")

    __class_getitem__(cls, param):
        if param is a tuple:             raise TypeError(f"{cls.__name__} takes exactly one type")
        if cls._parameterised:           raise TypeError
        if param is a types.GenericAlias: check = param.__origin__;  pname = repr(param)
        elif param is a class:            check = param;             pname = param.__name__
        else:                             raise TypeError
        key = (cls, param)
        if key not in cache:
            cache[key] = type(f"{cls.__name__}[{pname}]", (cls,),
                              {"item_type": param, "_check_type": check, "_parameterised": True})
        return cache[key]
```
