import time
from collections import OrderedDict


class TTLCache:
    """Bounded cache: entries expire after `ttl` seconds; the least recently used entry is dropped when full."""

    def __init__(self, maxsize=128, ttl=60.0, now=time.monotonic):
        self.maxsize, self.ttl, self.now = maxsize, ttl, now
        self._items = OrderedDict()            # key -> (expires_at, value)
        self.hits = self.misses = 0

    def get(self, key, default=None):
        # TODO: miss if missing or expired (remove expired entries); on a hit move the key to the end
        return default

    def set(self, key, value, ttl=None):
        # TODO: store (expires_at, value), mark as most recently used, evict while too big
        pass

    def delete(self, key):
        # TODO
        pass

    def __len__(self):
        return 0

    @property
    def hit_ratio(self):
        # TODO: hits / (hits + misses), 0.0 when there were no gets
        return 0.0
