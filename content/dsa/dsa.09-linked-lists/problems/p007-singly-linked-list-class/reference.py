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
        cur = self.head
        while cur is not None:
            yield cur.val
            cur = cur.next

    def push_front(self, val):
        node = ListNode(val, self.head)
        self.head = node
        if self.tail is None:
            self.tail = node
        self._size += 1

    def push_back(self, val):
        node = ListNode(val)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def pop_front(self):
        if self.head is None:
            raise IndexError("pop from empty list")
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return node.val

    def remove(self, val):
        prev, cur = None, self.head
        while cur is not None:
            if cur.val == val:
                if prev is None:
                    self.head = cur.next
                else:
                    prev.next = cur.next
                if cur is self.tail:
                    self.tail = prev
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False
