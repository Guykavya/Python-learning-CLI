## Approach

Chapter section 3. Every node stores the sum of its range `[lo, hi)`; the children split it at `mid = (lo + hi) // 2`. A query covers `[l, r)` with a few whole nodes:

1. **No overlap** (`r <= lo or hi <= l`): return 0, the identity of `+`.
2. **Inside** (`l <= lo and hi <= r`): return the stored sum, do not go deeper.
3. **Partial**: ask both children and add their answers.

```python
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
```

With half-open ranges, `[4, 6)` and the query `[2, 4)` share no element although the number 4 appears in both: hence `<=` in the "no overlap" test.

## Complexity

Build `O(n)` (fewer than `2n` nodes, each made once). Query `O(log n)`: at most two nodes per level are partial (chapter section 4), so at most four are visited per level. Memory `4n`.

## Another way

The iterative tree of p006 (size `2n`, no recursion) is shorter and faster in Python. For a static array without updates, plain prefix sums (p001) are simpler still: this problem builds the tree because the next one adds updates.
