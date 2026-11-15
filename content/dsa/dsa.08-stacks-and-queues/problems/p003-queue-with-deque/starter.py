from collections import deque


class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, x):
        pass  # TODO

    def dequeue(self):
        pass  # TODO: raise IndexError("dequeue from empty queue") when empty

    def front(self):
        pass  # TODO: raise IndexError("front of empty queue") when empty

    def is_empty(self):
        return True  # TODO

    def __len__(self):
        return 0  # TODO
