from collections import deque


class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, x):
        self._items.append(x)

    def dequeue(self):
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def front(self):
        if not self._items:
            raise IndexError("front of empty queue")
        return self._items[0]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)
