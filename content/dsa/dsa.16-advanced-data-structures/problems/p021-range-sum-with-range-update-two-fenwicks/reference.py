class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        """Sum of a[0:r]."""
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total


class RangeAddSum:
    """Range add, range sum with two Fenwick trees. Half-open [l, r)."""

    def __init__(self, a):
        self.n = n = len(a)
        self.base = [0] * (n + 1)                 # plain prefix sums of the original values
        for i, x in enumerate(a):
            self.base[i + 1] = self.base[i] + x
        self.b1 = Fenwick(n)                      # over d[j]
        self.b2 = Fenwick(n)                      # over j * d[j]

    def add(self, l, r, v):
        self.b1.add(l, v)
        self.b2.add(l, v * l)
        if r < self.n:
            self.b1.add(r, -v)
            self.b2.add(r, -v * r)

    def prefix(self, p):
        """Sum of a[0:p]."""
        return self.base[p] + p * self.b1.prefix(p) - self.b2.prefix(p)

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l)
