class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class LinkedStack:
    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, val):
        pass  # TODO

    def pop(self):
        raise IndexError("pop from empty stack")  # TODO

    def peek(self):
        raise IndexError("peek at empty stack")  # TODO

    def __len__(self):
        return self._size


class LinkedQueue:
    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def enqueue(self, val):
        pass  # TODO

    def dequeue(self):
        raise IndexError("dequeue from empty queue")  # TODO

    def peek(self):
        raise IndexError("peek at empty queue")  # TODO

    def __len__(self):
        return self._size
