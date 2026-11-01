## Hint 1

Which dictionary type removes an entry by itself when its value dies? When you look a key up,
how do you tell "dead or never stored" from "alive" in one step, without a `KeyError`? After
creating a new object, which reference do you return: the local variable or a fresh lookup?

## Hint 2

```
__init__: self._entries = weakref.WeakValueDictionary()

get(key):
    obj = self._entries.get(key)        # None if missing or dead
    if obj is not None: hits += 1; return obj
    misses += 1
    obj = self.factory(key)             # a strong local reference
    self._entries[key] = obj
    return obj                          # the local, not self._entries[key]

__len__      -> len(self._entries)
__contains__ -> key in self._entries
```
