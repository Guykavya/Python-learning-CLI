## Approach

The dictionary answers "where is this key's node?" in `O(1)`. The doubly linked list keeps the usage order: the node after the head sentinel is the most recently used, the node before the tail sentinel the least. "Use a key" means: unlink its node and push it to the front, both `O(1)` because the node knows its `prev` and `next`. Eviction takes `tail.prev`, and the key stored in that node tells us which dictionary entry to delete.

## Hand trace (capacity 3, real output of the reference)

```text
put a 1
put b 2
put c 3
get a -> 1
put d 4
get b -> -1
put c 30
put e 5
get a -> -1
get c -> 30
get d -> 4
get e -> 5
```

Order from most to least recent after each step: `a`; `b a`; `c b a`; `a c b` (get a); `d a c` (evicted `b`); unchanged (get b missed); `c d a` (c updated); `e c d` (evicted `a`); then the gets reorder them, all hits except `a`.

## Code

```python
class CacheNode:
    def __init__(self, key=None, val=None):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.nodes = {}                      # key -> node
        self.head = CacheNode()              # sentinel: after it comes the most recently used
        self.tail = CacheNode()              # sentinel: before it comes the least recently used
        self.head.next = self.tail
        self.tail.prev = self.head

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _push_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        node = self.nodes.get(key)
        if node is None:
            return -1
        self._unlink(node)                   # it is now the most recently used
        self._push_front(node)
        return node.val

    def put(self, key, value):
        node = self.nodes.get(key)
        if node is not None:                 # update: new value, most recently used
            node.val = value
            self._unlink(node)
            self._push_front(node)
            return
        if len(self.nodes) == self.capacity:
            lru = self.tail.prev             # the least recently used node
            self._unlink(lru)
            del self.nodes[lru.key]          # the node stores its key for exactly this line
        node = CacheNode(key, value)
        self.nodes[key] = node
        self._push_front(node)
```

## Complexity

`get` and `put` are `O(1)`: one dictionary operation and a constant number of pointer changes. Memory: `O(capacity)` nodes and dictionary entries.

## Another way

`collections.OrderedDict` is a dictionary plus a doubly linked list inside, and has `move_to_end(key)` and `popitem(last=False)`: the whole cache in a dozen lines (that is the test's model). Python's own `functools.lru_cache` decorator uses the same dict-plus-linked-list design in C. Since Python 3.7 a plain `dict` also keeps insertion order, so `d[k] = d.pop(k)` moves a key to the end and `next(iter(d))` is the oldest key; that works too, but the linked list is what this problem is about.
