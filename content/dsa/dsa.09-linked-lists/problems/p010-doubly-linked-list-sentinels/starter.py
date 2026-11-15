class DNode:
    def __init__(self, val=None):
        self.val = val
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = DNode()              # sentinel before the first item
        self.tail = DNode()              # sentinel after the last item
        # TODO: link the two sentinels to each other
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        return iter([])  # TODO: yield values from head.next up to (not including) tail

    def append(self, val):
        return None  # TODO: return the new node

    def appendleft(self, val):
        return None  # TODO

    def remove_node(self, node):
        return None  # TODO

    def pop(self):
        raise IndexError("pop from empty list")  # TODO

    def popleft(self):
        raise IndexError("pop from empty list")  # TODO
