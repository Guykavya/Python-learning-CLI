import math
import threading
import time


class MiniRedis:
    """The string commands of Redis, in-process, with an injected clock."""

    def __init__(self, now=time.time):
        self.now = now
        self._data = {}          # key -> str
        self._expires = {}       # key -> deadline (seconds, same clock as now())
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
