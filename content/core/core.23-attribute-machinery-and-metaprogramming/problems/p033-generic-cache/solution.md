## Approach

`Box[int]` calls `Box.__class_getitem__(int)`. Normally (for `list[int]`) that returns a
`types.GenericAlias`, a description that does nothing at run time. We return a **real
subclass** instead, built with `type(name, (cls,), namespace)`. The namespace only needs class
attributes; the inherited `put` reads `self._check_type` and so checks the right type for each
generated class.

Three details make it correct:

- **Cache key `(cls, param)`.** The cache dict lives on `Box`, so every subclass sees the same
  dict. With `param` alone as the key, `Special[int]` would return `Box[int]`.
- **Tuples.** `Box[int, str]` passes *one* argument, the tuple `(int, str)`.
- **Aliases.** `list[int]` is a `types.GenericAlias`; `isinstance(x, list[int])` raises
  `TypeError`. We keep the alias as `item_type` (for the name and for users) and check against its
  `__origin__`, `list`.

## Code

```python
import types

_EMPTY = object()


class Box:
    item_type = object
    _check_type = object
    _parameterised = False
    _cache = {}                     # shared by all subclasses, so the key includes the class

    def __init__(self):
        self._value = _EMPTY

    def put(self, value):
        if not isinstance(value, self._check_type):
            raise TypeError(
                f"{type(self).__name__} accepts {_name_of(self.item_type)}, not {type(value).__name__}"
            )
        self._value = value

    def get(self):
        if self._value is _EMPTY:
            raise LookupError("box is empty")
        return self._value

    def __repr__(self):
        inside = "empty" if self._value is _EMPTY else repr(self._value)
        return f"{type(self).__name__}({inside})"

    def __class_getitem__(cls, param):
        if isinstance(param, tuple):
            raise TypeError(f"{cls.__name__} takes exactly one type")
        if cls._parameterised:
            raise TypeError(f"{cls.__name__} is already parameterised")
        if isinstance(param, types.GenericAlias):
            check = param.__origin__
        elif isinstance(param, type):
            check = param
        else:
            raise TypeError(f"{cls.__name__}[...] needs a class, got {param!r}")
        key = (cls, param)
        if key not in Box._cache:
            name = f"{cls.__name__}[{_name_of(param)}]"
            Box._cache[key] = type(name, (cls,), {
                "item_type": param,
                "_check_type": check,
                "_parameterised": True,
                "__module__": cls.__module__,
            })
        return Box._cache[key]


def _name_of(param):
    if isinstance(param, types.GenericAlias):
        return repr(param)          # list[int]
    return param.__name__           # int, Box[int]
```

Why the cache matters: without it, `Box[int]()` and another `Box[int]()` would be instances of
two *different* classes, so `isinstance(a, Box[int])` would be `False` for a box made a moment
earlier, and nested boxes (`Box[Box[int]]`) could never accept anything.

## Complexity

`Box[T]` is an O(1) dict lookup after the first time (creating the class once is O(1) too).
`put` is one `isinstance` call.

## Another way

Keep a cache per class in the class's **own** `__dict__` (`vars(cls).setdefault`-style), keyed by
`param` alone, and build the class with a class statement inside `__class_getitem__`:

```python
if "_made" not in vars(cls):
    cls._made = {}
made = vars(cls)["_made"]
if param not in made:
    class Param(cls):
        item_type = param
    Param.__name__ = Param.__qualname__ = f"{cls.__name__}[{pname}]"
    made[param] = Param
return made[param]
```

`functools.cache` on a helper function `_make(cls, param)` would also work, since both
arguments are hashable. For static type checking, the standard tool is `typing.Generic[T]`
(core.16); it creates aliases, not checking classes, and that is usually what you want: real
runtime checks cost time on every `put`.
