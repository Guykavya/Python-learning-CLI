class LazySum:
    """Range add, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.a = list(a)

    def add(self, l, r, v):
        for i in range(l, r):                # O(r - l): too slow for long ranges
            self.a[i] += v

    def query(self, l, r):
        return sum(self.a[l:r])
