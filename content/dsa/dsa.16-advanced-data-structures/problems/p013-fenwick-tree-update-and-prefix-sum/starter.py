class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        """a[i] += v"""

    def prefix(self, r):
        """Sum of a[0:r]."""
        return 0
