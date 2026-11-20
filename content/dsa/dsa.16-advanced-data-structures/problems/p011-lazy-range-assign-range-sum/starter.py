class AssignSum:
    """Range assign, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.s = [0] * (4 * self.n)
        self.tag = [0] * (4 * self.n)          # 0 means "no pending assignment"... but 0 is also a value
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
        self.s[node] = v * (hi - lo)
        self.tag[node] = v

    def _push(self, node, lo, hi):
        if self.tag[node]:
            mid = (lo + hi) // 2
            self._apply(2 * node, lo, mid, self.tag[node])
            self._apply(2 * node + 1, mid, hi, self.tag[node])
            self.tag[node] = 0

    def assign(self, l, r, v):
        self._assign(1, 0, self.n, l, r, v)

    def _assign(self, node, lo, hi, l, r, v):
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, lo, hi, v)
            return
        self._push(node, lo, hi)
        mid = (lo + hi) // 2
        self._assign(2 * node, lo, mid, l, r, v)
        self._assign(2 * node + 1, mid, hi, l, r, v)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.s[node]
        self._push(node, lo, hi)
        mid = (lo + hi) // 2
        return self._query(2 * node, lo, mid, l, r) + self._query(2 * node + 1, mid, hi, l, r)
