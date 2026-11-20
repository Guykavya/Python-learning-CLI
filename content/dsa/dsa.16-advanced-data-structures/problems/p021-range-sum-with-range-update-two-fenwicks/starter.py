class RangeAddSum:
    """Range add, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.a = list(a)

    def add(self, l, r, v):
        for i in range(l, r):
            self.a[i] += v

    def range_sum(self, l, r):
        return sum(self.a[l:r])
