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

    def set(self, key, value, ex=None, nx=False):
        # TODO
        return None

    def get(self, key):
        # TODO
        return None

    def delete(self, *keys):
        return 0

    def exists(self, *keys):
        return 0

    def incr(self, key, amount=1):
        return 0

    def expire(self, key, seconds):
        return False

    def ttl(self, key):
        return -2
