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
