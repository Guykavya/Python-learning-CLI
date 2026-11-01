## Approach

Let `WeakValueDictionary` do the bookkeeping: it removes an entry when its value is freed, so
`len` and `in` are always about live objects. `get` uses `.get(key)` so that a missing key and a
dead one both come back as `None`. The new object is held in a local variable while it is stored
and returned, so it is never without a strong reference.

## Code

```python
import weakref


class Cache:
    def __init__(self, factory):
        self.factory = factory
        self.hits = 0
        self.misses = 0
        self._entries = weakref.WeakValueDictionary()

    def get(self, key):
        obj = self._entries.get(key)
        if obj is not None:
            self.hits += 1
            return obj
        self.misses += 1
        obj = self.factory(key)
        self._entries[key] = obj
        return obj

    def __len__(self):
        return len(self._entries)

    def __contains__(self, key):
        return key in self._entries
```

## Complexity

O(1) average for `get`, `len` and `in`, like a normal dict.

## Another way

Build it yourself from a plain dict of `weakref.ref` objects, which shows what
`WeakValueDictionary` does inside:

```python
def get(self, key):
    ref = self._refs.get(key)
    obj = ref() if ref is not None else None
    if obj is not None:
        self.hits += 1
        return obj
    self.misses += 1
    obj = self.factory(key)
    self._refs[key] = weakref.ref(obj, lambda r, key=key: self._refs.pop(key, None))
    return obj
```

The callback removes the dead entry. (The real class is more careful: the callback must not
remove a *newer* entry stored under the same key.) Use a weak cache for big shared objects
(images, parsed files); use `functools.lru_cache` when you want values kept even while unused.
