class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    # Bug 1: the user's index is 0-based but the cells are 1-based, so add must start at i + 1;
    #        with i = 0 the step 0 & 0 (or 0 & -0) is 0 and the loop never ends.
    # Bug 2: i & i is i itself, so the loop doubled i and skipped cells that cover the position;
    #        the step to the next covering cell is the lowest set bit, i & -i.
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
        return self.prefix(r) - self.prefix(l)
