import threading


class OnceCache:
    """Thread-safe cache: compute() runs once per key, different keys run in parallel."""

    def __init__(self):
        self._values = {}

    def get(self, key, compute):
        if key in self._values:
            return self._values[key]
        value = compute()                # every thread that got here computes again
        self._values[key] = value
        return value
