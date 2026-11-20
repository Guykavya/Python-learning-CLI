class SegTree:
    """Sum segment tree. Half-open ranges [l, r), 0-indexed."""

    def __init__(self, a):
        self.n = len(a)
        self.a = list(a)
        self.t = [0] * (4 * self.n)

    def query(self, l, r):
        """Sum of a[l:r]."""
        return sum(self.a[l:r])
