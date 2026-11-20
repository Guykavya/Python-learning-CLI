class Fenwick:
    """Point add, range sum. Public interface 0-indexed, half-open."""

    def __init__(self, n, a=None):
        self.n = n
        self.t = [0] * (n + 1)
        if a is not None:
            for i, x in enumerate(a):        # n calls to add: O(n log n)
                self.add(i, x)

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l - 1)

    def get(self, i):
        return self.range_sum(i, i + 1)

    def set(self, i, v):
        self.add(i, v)
