import threading
import time


class Counter:
    """A counter that many threads can increment at the same time."""

    def __init__(self):
        self._value = 0

    def increment(self):
        current = self._value
        time.sleep(0)            # stands for "other work" between the read and the write
        self._value = current + 1

    @property
    def value(self):
        return self._value
