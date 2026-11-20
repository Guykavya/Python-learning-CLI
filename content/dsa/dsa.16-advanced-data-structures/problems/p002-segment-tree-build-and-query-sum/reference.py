class SegTree:
    """Sum segment tree. Half-open ranges [l, r), 0-indexed."""

    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * (4 * self.n)
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:                       # a leaf
            self.t[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:                 # no overlap
            return 0
        if l <= lo and hi <= r:                # node fully inside the query
            return self.t[node]
        mid = (lo + hi) // 2                   # partial overlap: ask both children
        return self._query(2 * node, lo, mid, l, r) + self._query(2 * node + 1, mid, hi, l, r)
