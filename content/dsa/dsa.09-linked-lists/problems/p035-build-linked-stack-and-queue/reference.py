class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class LinkedStack:
    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, val):
        self._top = ListNode(val, self._top)     # the new node points at the old top
        self._size += 1

    def pop(self):
        if self._top is None:
            raise IndexError("pop from empty stack")
        node = self._top
        self._top = node.next
        self._size -= 1
        return node.val

    def peek(self):
        if self._top is None:
            raise IndexError("peek at empty stack")
        return self._top.val

    def __len__(self):
        return self._size


class LinkedQueue:
    def __init__(self):
        self._head = None                        # next to leave
        self._tail = None                        # last to arrive
        self._size = 0

    def enqueue(self, val):
        node = ListNode(val)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def dequeue(self):
        if self._head is None:
            raise IndexError("dequeue from empty queue")
        node = self._head
        self._head = node.next
        if self._head is None:                   # the queue became empty: the tail must follow
            self._tail = None
        self._size -= 1
        return node.val

    def peek(self):
        if self._head is None:
            raise IndexError("peek at empty queue")
        return self._head.val

    def __len__(self):
        return self._size
