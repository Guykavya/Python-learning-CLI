class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        while i <= self.n:
            self.t[i] += v
            i += i & i

    def prefix(self, r):
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l)
