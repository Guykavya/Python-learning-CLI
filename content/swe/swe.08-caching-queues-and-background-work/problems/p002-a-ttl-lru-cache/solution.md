## Approach

An `OrderedDict` keeps keys in the order they were last used. `get` checks the expiry time, removes an expired entry and counts a miss; on a hit it moves the key to the end (most recently used). `set` stores `(expires_at, value)`, moves the key to the end, then pops from the front while the cache is too big.

```python
import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, maxsize=128, ttl=60.0, now=time.monotonic):
        self.maxsize, self.ttl, self.now = maxsize, ttl, now
        self._items = OrderedDict()            # key -> (expires_at, value)
        self.hits = self.misses = 0

    def get(self, key, default=None):
        entry = self._items.get(key)
        if entry is None or entry[0] <= self.now():
            if entry is not None:
                del self._items[key]
            self.misses += 1
            return default
        self._items.move_to_end(key)
        self.hits += 1
        return entry[1]

    def set(self, key, value, ttl=None):
        self._items[key] = (self.now() + (self.ttl if ttl is None else ttl), value)
        self._items.move_to_end(key)
        while len(self._items) > self.maxsize:
            self._items.popitem(last=False)

    def delete(self, key):
        self._items.pop(key, None)

    def __len__(self):
        return len(self._items)

    @property
    def hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0.0
```

## Complexity

`get`, `set` and `delete` are O(1): dictionary lookups plus `move_to_end`/`popitem`, which are O(1) in `OrderedDict`. Memory is O(maxsize). Expired entries that are never read again stay until they are evicted; that is the price of lazy expiry (Redis also runs a background sweep for this reason).

## Another way

`functools.lru_cache` gives LRU without expiry for function results. The `cachetools` package has a ready `TTLCache` (not installed here). With a plain `dict`, you could also use its insertion order: `d.pop(key)` then `d[key] = entry` moves a key to the end, and `next(iter(d))` is the least recently used.
