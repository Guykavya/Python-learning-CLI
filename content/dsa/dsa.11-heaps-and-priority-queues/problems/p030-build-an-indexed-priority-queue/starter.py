class IndexedPQ:
    """A min-priority queue on a hand-written heap that knows the position of every key.

    Do not import heapq, bisect or sorted: write the sifts yourself.
    """

    def __init__(self):
        self.keys = []                       # keys[i] is the key at heap position i
        self.prios = []                      # prios[i] is its priority
        self.pos = {}                        # key -> position in the two lists

    def __len__(self):
        return 0

    def __contains__(self, key):
        return False

    def stored(self):
        return 0

    def peek(self):
        raise IndexError("peek from an empty queue")

    def priority(self, key):
        raise KeyError(key)

    def push(self, key, priority):
        pass

    def update(self, key, priority):
        pass

    def remove(self, key):
        pass

    def pop_min(self):
        raise IndexError("pop from an empty queue")
