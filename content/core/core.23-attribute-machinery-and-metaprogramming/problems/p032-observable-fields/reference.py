class Field:
    def __init__(self, default=None):
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, self.default)

    def __set__(self, obj, value):
        old = self.__get__(obj)
        if old == value:
            return
        obj.__dict__[self.name] = value
        _history(obj).append((self.name, old, value))
        _notify(obj, self.name, old, value)


class Observable:
    _fields = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        names = list(cls._fields)                       # the parent's fields first
        for name, value in vars(cls).items():
            if isinstance(value, Field) and name not in names:
                names.append(name)
        cls._fields = tuple(names)

    def __init__(self, **values):
        for name, value in values.items():
            if name not in self._fields:
                raise TypeError(f"{type(self).__name__} has no field {name!r}")
            self.__dict__[name] = value                 # initial value: no history, no events


def _history(obj):
    return obj.__dict__.setdefault("_history", [])


def _subscribers(obj):
    return obj.__dict__.setdefault("_subscribers", [])


def _notify(obj, name, old, new):
    for callback in list(_subscribers(obj)):
        callback(obj, name, old, new)


def fields(obj_or_cls):
    return obj_or_cls._fields


def subscribe(obj, callback):
    _subscribers(obj).append(callback)
    return callback


def unsubscribe(obj, callback):
    _subscribers(obj).remove(callback)


def history(obj):
    return list(_history(obj))


def undo(obj):
    changes = _history(obj)
    if not changes:
        return None
    name, old, new = changes.pop()
    obj.__dict__[name] = old
    _notify(obj, name, new, old)
    return (name, old, new)
