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
        # TODO: two sentinels (head = most recent side, tail = least recent side)

    def get(self, key):
        return -1  # TODO

    def put(self, key, value):
        pass  # TODO
