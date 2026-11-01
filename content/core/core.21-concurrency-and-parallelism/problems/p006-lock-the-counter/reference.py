import threading
import time


class Counter:
    """A counter that many threads can increment at the same time."""

    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            current = self._value
            time.sleep(0)            # stands for "other work" between the read and the write
            self._value = current + 1

    @property
    def value(self):
        with self._lock:
            return self._value
