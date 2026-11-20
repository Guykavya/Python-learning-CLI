import time
from collections import OrderedDict


class TTLCache:
    """Bounded cache: entries expire after `ttl` seconds; the least recently used entry is dropped when full."""

    def __init__(self, maxsize=128, ttl=60.0, now=time.monotonic):
        self.maxsize, self.ttl, self.now = maxsize, ttl, now
        self._items = OrderedDict()            # key -> (expires_at, value)
        self.hits = self.misses = 0

    def get(self, key, default=None):
        entry = self._items.get(key)
        if entry is None or entry[0] <= self.now():
            if entry is not None:
                del self._items[key]           # expired: remove it lazily
            self.misses += 1
            return default
        self._items.move_to_end(key)           # most recently used
        self.hits += 1
        return entry[1]

    def set(self, key, value, ttl=None):
        self._items[key] = (self.now() + (self.ttl if ttl is None else ttl), value)
        self._items.move_to_end(key)
        while len(self._items) > self.maxsize:
            self._items.popitem(last=False)    # evict the least recently used

    def delete(self, key):
        self._items.pop(key, None)

    def __len__(self):
        return len(self._items)

    @property
    def hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0.0
