import bisect


class MinuteBag:
    """Multiset of values 0..m-1 with k-th smallest."""

    def __init__(self, m):
        self.items = []

    def insert(self, v):
        bisect.insort(self.items, v)

    def remove(self, v):
        self.items.remove(v)
        return True

    def size(self):
        return len(self.items)

    def kth(self, k):
        return self.items[k - 1]
