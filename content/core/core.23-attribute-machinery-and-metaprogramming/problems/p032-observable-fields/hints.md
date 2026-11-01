## Hint 1

Every assignment `s.volume = 7` calls `Field.__set__(descriptor, s, 7)`. So the descriptor is the
one place that sees every change: it knows the object, its own name (from `__set_name__`), the
old value (whatever `__get__` would return now) and the new one.

Where should per-object things live: the value, the history list, the subscriber list? The
descriptor is shared by every `Settings` object, so not there. What does every object have that
is its own?

For `__init__`: if it used `setattr`, the initial values would go through `__set__` and be recorded.
How can it put a value in place without going through the descriptor?

## Hint 2

```
Field.__set__(self, obj, value):
    old = self.__get__(obj)                    # default if never set
    if old == value: return
    obj.__dict__[self.name] = value
    history_list(obj).append((self.name, old, value))
    for cb in list(subscribers(obj)): cb(obj, self.name, old, value)

history_list(obj):  return obj.__dict__.setdefault("_history", [])
subscribers(obj):   return obj.__dict__.setdefault("_subscribers", [])

Observable.__init_subclass__(cls, **kw):
    super().__init_subclass__(**kw)
    names = list(cls._fields)                  # inherited from the parent (start: () on Observable)
    for name, value in vars(cls).items():
        if isinstance(value, Field) and name not in names: names.append(name)
    cls._fields = tuple(names)

undo(obj):
    if history empty: return None
    name, old, new = history.pop()
    obj.__dict__[name] = old                   # direct write: no new history entry
    notify subscribers with (obj, name, new, old)
    return (name, old, new)
```
