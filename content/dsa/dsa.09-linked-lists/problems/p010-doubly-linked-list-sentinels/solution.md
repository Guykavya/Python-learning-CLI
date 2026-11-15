## Approach

Write two private helpers and build everything else from them:

- `_insert_after(node, val)` links a new node between `node` and `node.next`. The new node's own pointers are set first (they read the old links), then the neighbours are pointed at it.
- `remove_node(node)` makes the two neighbours point at each other, then cuts the node free.

`append` inserts after `tail.prev`, `appendleft` after `head`; `pop` removes `tail.prev`, `popleft` removes `head.next`. Because the sentinels are always there, no method needs an `if` for "first node", "last node" or "only node", only the empty check before a pop.

## Code

```python
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
```

## Complexity

Every method is `O(1)`: a fixed number of pointer changes, no walking. Memory: two pointers per item plus two sentinels.

## Another way

Without sentinels, `head` and `tail` are `None` for an empty list, and every method needs branches: "is the list empty?", "is this the first node?", "is this the last node?". That is how most textbook versions look, and those branches are exactly where the bugs live. Python's own `collections.deque` is a doubly linked list of **blocks** of 64 items, which saves memory and keeps `O(1)` ends, but it gives you no node handles, so it cannot remove from the middle in `O(1)`. That is why LRU caches (problem 34) build their own list.
