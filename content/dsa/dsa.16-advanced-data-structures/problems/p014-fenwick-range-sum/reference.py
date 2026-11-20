class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n, a=None):
        self.n = n
        self.t = [0] * (n + 1)              # t[0] is never used
        if a is not None:                   # O(n) build: push each cell into its parent once
            for k in range(1, n + 1):
                self.t[k] += a[k - 1]
                parent = k + (k & -k)
                if parent <= n:
                    self.t[parent] += self.t[k]

    def add(self, i, v):
        """a[i] += v"""
        i += 1                              # to 1-indexed
        while i <= self.n:
            self.t[i] += v
            i += i & -i                     # the next cell that covers position i

    def prefix(self, r):
        """Sum of a[0:r]."""
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r                     # drop the lowest set bit
        return total

    def range_sum(self, l, r):
        """Sum of a[l:r]."""
        return self.prefix(r) - self.prefix(l)

    def get(self, i):
        """a[i]"""
        return self.range_sum(i, i + 1)

    def set(self, i, v):
        """a[i] = v"""
        self.add(i, v - self.get(i))
