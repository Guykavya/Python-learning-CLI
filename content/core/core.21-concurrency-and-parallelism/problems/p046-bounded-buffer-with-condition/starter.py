import threading
from collections import deque


class BoundedBuffer:
    """A thread-safe FIFO buffer that holds at most `capacity` items."""

    def __init__(self, capacity):
        self.capacity = capacity
        self._items = deque()
        self._cond = threading.Condition()

    def put(self, item, timeout=None):
        raise NotImplementedError("with the condition: wait_for room, append, notify_all")

    def get(self, timeout=None):
        raise NotImplementedError("with the condition: wait_for an item, popleft, notify_all")

    def __len__(self):
        with self._cond:
            return len(self._items)
