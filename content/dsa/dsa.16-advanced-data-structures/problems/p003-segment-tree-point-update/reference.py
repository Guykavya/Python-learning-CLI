class SegTree:
    """Sum segment tree with point update. Half-open ranges [l, r), 0-indexed."""

    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * (4 * self.n)
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.t[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.t[node]
        mid = (lo + hi) // 2
        return self._query(2 * node, lo, mid, l, r) + self._query(2 * node + 1, mid, hi, l, r)

    def update(self, i, v):
        self._update(1, 0, self.n, i, v)

    def _update(self, node, lo, hi, i, v):
        if hi - lo == 1:                       # the leaf of position i
            self.t[node] = v
            return
        mid = (lo + hi) // 2
        if i < mid:
            self._update(2 * node, lo, mid, i, v)
        else:
            self._update(2 * node + 1, mid, hi, i, v)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]   # fix on the way back up
