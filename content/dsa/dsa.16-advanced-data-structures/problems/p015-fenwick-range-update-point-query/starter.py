class RangeAdder:
    """Range add, point query. Half-open [l, r)."""

    def __init__(self, a):
        self.a = list(a)

    def add(self, l, r, v):
        for i in range(l, r):                 # O(r - l)
            self.a[i] += v

    def get(self, i):
        return self.a[i]
