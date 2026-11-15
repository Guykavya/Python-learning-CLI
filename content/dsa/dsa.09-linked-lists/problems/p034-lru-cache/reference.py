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
