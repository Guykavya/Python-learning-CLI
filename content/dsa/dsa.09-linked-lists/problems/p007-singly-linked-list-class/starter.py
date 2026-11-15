class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        # TODO: yield the values from head to tail
        return iter([])

    def push_front(self, val):
        pass  # TODO

    def push_back(self, val):
        pass  # TODO: O(1) with self.tail

    def pop_front(self):
        raise IndexError("pop from empty list")  # TODO

    def remove(self, val):
        return False  # TODO: first match only; fix head, tail and size
