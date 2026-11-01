import threading
from collections import deque


class BoundedBuffer:
    """A thread-safe FIFO buffer that holds at most `capacity` items."""

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._items = deque()
        self._cond = threading.Condition()

    def put(self, item, timeout=None):
        with self._cond:
            has_room = self._cond.wait_for(lambda: len(self._items) < self.capacity, timeout)
            if not has_room:
                raise TimeoutError("buffer is full")
            self._items.append(item)
            self._cond.notify_all()        # wake getters (and anyone re-checking)

    def get(self, timeout=None):
        with self._cond:
            has_item = self._cond.wait_for(lambda: len(self._items) > 0, timeout)
            if not has_item:
                raise TimeoutError("buffer is empty")
            item = self._items.popleft()
            self._cond.notify_all()        # wake putters waiting for room
            return item

    def __len__(self):
        with self._cond:
            return len(self._items)
