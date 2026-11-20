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


def count_inversions(a):
    ranks = {v: i for i, v in enumerate(sorted(set(a)))}     # coordinate compression
    bit = Fenwick(len(ranks))                                 # how many earlier elements have each rank
    inversions = 0
    for seen, x in enumerate(a):                              # seen = number of earlier elements
        k = ranks[x]
        inversions += seen - bit.prefix(k + 1)                # earlier elements strictly greater than x
        bit.add(k, 1)
    return inversions
