"""Course helpers for this problem, copied from the chapter (swe.08). The tests receive them as fixtures.
Your solution never imports this file: everything it needs arrives as a function argument."""
import fnmatch
import json
import math
import random
import signal
import sqlite3
import threading
import time
from contextlib import closing

import pytest





class FakeClock:
    """Time that moves only when a test says so. Call it to read the time: clock() -> seconds."""

    def __init__(self, start=0.0):
        self.t = float(start)

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds
        return self.t



class MiniRedis:
    """A small in-process stand-in for the Redis commands used in this chapter."""

    def __init__(self, now=time.time):
        self.now = now
        self._data, self._expires = {}, {}
        self._lock = threading.RLock()                       # one command at a time, like Redis

    # ---- internals
    def _alive(self, key):
        deadline = self._expires.get(key)
        if deadline is not None and deadline <= self.now():
            self._data.pop(key, None)
            self._expires.pop(key, None)
        return key in self._data

    def _get_typed(self, key, kind, create=None):
        if not self._alive(key):
            if create is None:
                return None
            self._data[key] = create()
        value = self._data[key]
        if not isinstance(value, kind):
            raise TypeError("WRONGTYPE Operation against a key holding the wrong kind of value")
        return value

    # ---- keys and strings
    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        with self._lock:
            exists = self._alive(key)
            if (nx and exists) or (xx and not exists):
                return None
            self._data[key] = str(value)
            self._expires.pop(key, None)
            if ex is not None:
                self._expires[key] = self.now() + ex
            elif px is not None:
                self._expires[key] = self.now() + px / 1000
            return True

    def get(self, key):
        with self._lock:
            return self._get_typed(key, str)

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
            current = self._get_typed(key, str)
            try:
                value = int(current or 0) + amount
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

    def keys(self, pattern="*"):
        with self._lock:
            return sorted(k for k in list(self._data) if self._alive(k) and fnmatch.fnmatch(k, pattern))

    def flushall(self):
        with self._lock:
            self._data.clear()
            self._expires.clear()
            return True

    # ---- hashes
    def hset(self, key, field=None, value=None, mapping=None):
        with self._lock:
            h = self._get_typed(key, dict, create=dict)
            items = dict(mapping or {})
            if field is not None:
                items[field] = value
            added = sum(1 for f in items if f not in h)
            h.update({f: str(v) for f, v in items.items()})
            return added

    def hget(self, key, field):
        with self._lock:
            h = self._get_typed(key, dict)
            return None if h is None else h.get(field)

    def hgetall(self, key):
        with self._lock:
            return dict(self._get_typed(key, dict) or {})

    def hincrby(self, key, field, amount=1):
        with self._lock:
            h = self._get_typed(key, dict, create=dict)
            h[field] = str(int(h.get(field, 0)) + amount)
            return int(h[field])

    # ---- lists
    def lpush(self, key, *values):
        with self._lock:
            lst = self._get_typed(key, list, create=list)
            for v in values:
                lst.insert(0, str(v))
            return len(lst)

    def rpush(self, key, *values):
        with self._lock:
            lst = self._get_typed(key, list, create=list)
            lst.extend(str(v) for v in values)
            return len(lst)

    def lpop(self, key):
        with self._lock:
            lst = self._get_typed(key, list)
            return lst.pop(0) if lst else None

    def rpop(self, key):
        with self._lock:
            lst = self._get_typed(key, list)
            return lst.pop() if lst else None

    def llen(self, key):
        with self._lock:
            return len(self._get_typed(key, list) or [])

    def lrange(self, key, start, stop):
        with self._lock:
            lst = self._get_typed(key, list) or []
            stop = len(lst) if stop == -1 else stop + 1          # Redis ranges include the end index
            return lst[start:stop]

    # ---- sets
    def sadd(self, key, *members):
        with self._lock:
            s = self._get_typed(key, set, create=set)
            before = len(s)
            s.update(str(m) for m in members)
            return len(s) - before

    def srem(self, key, *members):
        with self._lock:
            s = self._get_typed(key, set) or set()
            removed = 0
            for m in members:
                if str(m) in s:
                    s.remove(str(m))
                    removed += 1
            return removed

    def smembers(self, key):
        with self._lock:
            return set(self._get_typed(key, set) or set())

    def sismember(self, key, member):
        with self._lock:
            return str(member) in (self._get_typed(key, set) or set())

    # ---- sorted sets
    def zadd(self, key, mapping):
        with self._lock:
            z = self._get_typed(key, _ZSet, create=_ZSet)
            added = sum(1 for m in mapping if m not in z)
            z.update({str(m): float(s) for m, s in mapping.items()})
            return added

    def zincrby(self, key, amount, member):
        with self._lock:
            z = self._get_typed(key, _ZSet, create=_ZSet)
            z[member] = z.get(member, 0.0) + amount
            return z[member]

    def zscore(self, key, member):
        with self._lock:
            return (self._get_typed(key, _ZSet) or {}).get(member)

    def zrange(self, key, start, stop, withscores=False, desc=False):
        with self._lock:
            z = self._get_typed(key, _ZSet) or {}
            ordered = sorted(z.items(), key=lambda kv: (kv[1], kv[0]), reverse=desc)
            stop = len(ordered) if stop == -1 else stop + 1
            chosen = ordered[start:stop]
            return chosen if withscores else [m for m, _ in chosen]

    def zrevrange(self, key, start, stop, withscores=False):
        return self.zrange(key, start, stop, withscores=withscores, desc=True)

    def zrem(self, key, *members):
        with self._lock:
            z = self._get_typed(key, _ZSet) or {}
            return sum(1 for m in members if z.pop(m, None) is not None)

    def zremrangebyscore(self, key, low, high):
        with self._lock:
            z = self._get_typed(key, _ZSet) or {}
            doomed = [m for m, score in z.items() if low <= score <= high]
            for m in doomed:
                del z[m]
            return len(doomed)

    def zcard(self, key):
        with self._lock:
            return len(self._get_typed(key, _ZSet) or {})


class _ZSet(dict):
    """member -> score."""




@pytest.fixture
def clock():
    return FakeClock(1000.0)


@pytest.fixture
def r(clock):
    """A MiniRedis whose time is the fake clock."""
    return MiniRedis(now=clock)


@pytest.fixture
def make_redis():
    """A factory: make_redis() gives a fresh, empty MiniRedis."""
    return lambda: MiniRedis()
