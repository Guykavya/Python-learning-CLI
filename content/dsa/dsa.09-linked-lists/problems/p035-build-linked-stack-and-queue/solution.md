## Approach

Both structures are one chain of nodes used at chosen ends.

- **Stack**: push and pop at the head. A new node points at the old top, and popping moves the top to `next`. One pointer and a size counter are enough.
- **Queue**: dequeue at the head (`O(1)`: move the head forward) and enqueue at the tail (`O(1)` thanks to the tail pointer). The reverse choice would need to remove the tail, which in a singly linked list means walking to the node before it (`O(n)`).

The only subtle moments are the border pictures of the queue: empty → one item (both pointers to the new node) and one item → empty (both pointers to `None`).

## Code

```python
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
```

## Complexity

Every operation is `O(1)`. Memory: one node per item (more than a Python list per item, see chapter section 14), but no resizing ever happens, so no single operation is ever slow.

## Another way

A **circular** singly linked list with only a `tail` pointer is enough for a queue: the head is `tail.next`. Enqueue inserts after the tail and moves the tail; dequeue removes `tail.next`. One pointer instead of two, at the price of slightly trickier code. A queue can also be built from two `LinkedStack`s (dsa.08, problem 22), with amortised `O(1)`.
