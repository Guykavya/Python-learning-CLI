## Approach

Chapter section 5: a segment tree needs only an **associative combine** and its **identity**. For minimum they are `min` and `+infinity`; everything else is the tree of p003.

```python
import math

INF = math.inf

class MinTree:
    """Point update, range query on half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.t = [INF] * (4 * self.n)
        if self.n > 0:
            self._build(1, 0, self.n, a)

    @staticmethod
    def _f(x, y):
        return min(x, y)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.t[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.t[node] = self._f(self.t[2 * node], self.t[2 * node + 1])

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return INF                      # the identity: never changes the answer
        if l <= lo and hi <= r:
            return self.t[node]
        mid = (lo + hi) // 2
        return self._f(self._query(2 * node, lo, mid, l, r), self._query(2 * node + 1, mid, hi, l, r))

    def update(self, i, v):
        self._update(1, 0, self.n, i, v)

    def _update(self, node, lo, hi, i, v):
        if hi - lo == 1:
            self.t[node] = v
            return
        mid = (lo + hi) // 2
        if i < mid:
            self._update(2 * node, lo, mid, i, v)
        else:
            self._update(2 * node + 1, mid, hi, i, v)
        self.t[node] = self._f(self.t[2 * node], self.t[2 * node + 1])
```

The identity matters: with `0`, `MinTree([5, 3, 8, 6]).query(1, 3)` would visit an "outside" node, take `min(0, ...)` and answer 0 instead of 3.

## Complexity

`O(n)` build, `O(log n)` per update and query, `4n` memory.

## Another way

For data that never changes, a sparse table (p023) answers range minimum in `O(1)`. For point updates the segment tree (or its iterative form, p006) is the standard tool; a Fenwick tree cannot do it, because a minimum cannot be "subtracted".
