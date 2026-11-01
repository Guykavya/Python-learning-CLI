## Approach

The descriptor is the single choke point for every change, so it does all the work: compare,
store, record, notify. Everything that belongs to one object (its values, its history, its
subscribers) is kept in that object's `__dict__`; the descriptor itself only knows its name and
default, which are the same for every object.

`Field` is a **data** descriptor (it has `__set__`), so `s.volume` always goes through
`Field.__get__` even though the value sits in `s.__dict__["volume"]` under the same name.

`__init_subclass__` runs once per subclass, after all `__set_name__` calls, so it can collect the
field names. It reads the parent's `_fields` first (normal attribute lookup finds the nearest
parent's tuple) and appends the new names from `vars(cls)`, which keeps definition order.

Writes that must stay quiet (`__init__` and `undo`) go straight into `obj.__dict__` and skip
the descriptor.

## Code

```python
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
```

`_notify` loops over a copy of the list, so a callback may unsubscribe itself while being called.

## Complexity

Each assignment is O(s) for s subscribers. `history` is O(h) because it copies. `undo` is O(s).
Class creation is O(f) for f fields.

## Another way

Keep history and subscribers **outside** the objects, in `weakref.WeakKeyDictionary` objects
keyed by the object. Then the object's `__dict__` holds only its field values (nothing that looks
like a field can clash with `_history`), and the bookkeeping disappears automatically when the
object is garbage collected. The cost: the objects must be hashable and weak-referenceable.

```python
import weakref

_hist = weakref.WeakKeyDictionary()

def _history(obj):
    return _hist.setdefault(obj, [])
```

A metaclass could collect the fields too, but `__init_subclass__` is lighter and enough here.
