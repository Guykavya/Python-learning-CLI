class SparseMin:
    """Static range minimum. Half-open [l, r), l < r."""

    def __init__(self, a):
        self.a = list(a)
        self.table = [list(a)]

    def query(self, l, r):
        return min(self.a[l:r])
