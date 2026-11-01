import threading


class OnceCache:
    """Thread-safe cache: compute() runs once per key, different keys run in parallel."""

    def __init__(self):
        self._values = {}
        self._key_locks = {}
        self._lock = threading.Lock()      # guards the two dicts, held only briefly

    def get(self, key, compute):
        with self._lock:
            if key in self._values:
                return self._values[key]
            key_lock = self._key_locks.setdefault(key, threading.Lock())

        with key_lock:                     # one computing thread per key
            with self._lock:               # someone may have finished while we waited
                if key in self._values:
                    return self._values[key]
            value = compute()              # slow work: no shared lock held
            with self._lock:
                self._values[key] = value
            return value
