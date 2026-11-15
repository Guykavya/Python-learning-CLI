class DNode:
    def __init__(self, val=None):
        self.val = val
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = DNode()              # sentinel before the first item
        self.tail = DNode()              # sentinel after the last item
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        cur = self.head.next
        while cur is not self.tail:
            yield cur.val
            cur = cur.next

    def _insert_after(self, node, val):
        new = DNode(val)
        new.prev = node
        new.next = node.next
        node.next.prev = new
        node.next = new
        self._size += 1
        return new

    def append(self, val):
        return self._insert_after(self.tail.prev, val)

    def appendleft(self, val):
        return self._insert_after(self.head, val)

    def remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None
        self._size -= 1
        return node.val

    def pop(self):
        if self._size == 0:
            raise IndexError("pop from empty list")
        return self.remove_node(self.tail.prev)

    def popleft(self):
        if self._size == 0:
            raise IndexError("pop from empty list")
        return self.remove_node(self.head.next)
