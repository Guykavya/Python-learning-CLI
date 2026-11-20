class LazySum:
    """Range add, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.s = [0] * (4 * self.n)      # s[node]  = true sum of the node's range
        self.lz = [0] * (4 * self.n)     # lz[node] = what the children still owe
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.s[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def _apply(self, node, lo, hi, v):
        self.s[node] += v * (hi - lo)
        self.lz[node] += v

    def _push(self, node, lo, hi):
        if self.lz[node]:
            mid = (lo + hi) // 2
            self._apply(2 * node, lo, mid, self.lz[node])
            self._apply(2 * node + 1, mid, hi, self.lz[node])
            self.lz[node] = 0

    def add(self, l, r, v):
        self._add(1, 0, self.n, l, r, v)

    def _add(self, node, lo, hi, l, r, v):
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, lo, hi, v)          # stop here and leave a note
            return
        self._push(node, lo, hi)                  # deliver the note before descending
        mid = (lo + hi) // 2
        self._add(2 * node, lo, mid, l, r, v)
        self._add(2 * node + 1, mid, hi, l, r, v)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.s[node]
        self._push(node, lo, hi)                  # a query that descends must push too
        mid = (lo + hi) // 2
        return self._query(2 * node, lo, mid, l, r) + self._query(2 * node + 1, mid, hi, l, r)
