## Approach

Two dictionaries: `_data` (key -> string) and `_expires` (key -> deadline). One helper, `_alive`, applies lazy expiry, and every command calls it first while holding one `RLock`, so each command is atomic like a Redis command.

```python
import math
import threading
import time


class MiniRedis:
    def __init__(self, now=time.time):
        self.now = now
        self._data, self._expires = {}, {}
        self._lock = threading.RLock()

    def _alive(self, key):
        deadline = self._expires.get(key)
        if deadline is not None and deadline <= self.now():
            self._data.pop(key, None)
            self._expires.pop(key, None)
        return key in self._data

    def set(self, key, value, ex=None, nx=False):
        with self._lock:
            if nx and self._alive(key):
                return None
            self._data[key] = str(value)
            self._expires.pop(key, None)
            if ex is not None:
                self._expires[key] = self.now() + ex
            return True

    def get(self, key):
        with self._lock:
            return self._data[key] if self._alive(key) else None

    def delete(self, *keys):
        with self._lock:
            removed = 0
            for key in keys:
                if self._alive(key):
                    del self._data[key]
                    self._expires.pop(key, None)
                    removed += 1
            return removed

    def exists(self, *keys):
        with self._lock:
            return sum(1 for key in keys if self._alive(key))

    def incr(self, key, amount=1):
        with self._lock:
            current = self._data[key] if self._alive(key) else "0"
            try:
                value = int(current) + amount
            except ValueError:
                raise ValueError("ERR value is not an integer or out of range") from None
            self._data[key] = str(value)
            return value

    def expire(self, key, seconds):
        with self._lock:
            if not self._alive(key):
                return False
            self._expires[key] = self.now() + seconds
            return True

    def ttl(self, key):
        with self._lock:
            if not self._alive(key):
                return -2
            deadline = self._expires.get(key)
            return -1 if deadline is None else math.ceil(deadline - self.now())
```

## Complexity

Every command is O(1) per key (dictionary operations). Lazy expiry costs nothing until a key is touched; the downside is that expired keys nobody reads again stay in memory. Real Redis adds a background sweep that samples keys with a deadline and deletes the expired ones.

## Another way

Store `(value, deadline)` tuples in one dictionary instead of two. It is a little shorter, but `incr` must then copy the deadline carefully, and `set` must remember to reset it; two dictionaries make "keep the TTL" versus "clear the TTL" explicit. In real code you use `redis-py` against a server, or `fakeredis` in tests (neither is installed here).
