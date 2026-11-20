class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)              # t[0] is never used

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


class RangeAdder:
    """Range add, point query. Half-open [l, r)."""

    def __init__(self, a):
        self.base = list(a)
        self.n = len(a)
        self.fw = Fenwick(self.n)               # a Fenwick tree over the difference array

    def add(self, l, r, v):
        self.fw.add(l, v)                       # from l on, everything is v higher ...
        if r < self.n:
            self.fw.add(r, -v)                  # ... and from r on, back to normal

    def get(self, i):
        return self.base[i] + self.fw.prefix(i + 1)
