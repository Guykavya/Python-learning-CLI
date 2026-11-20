## Approach

Chapter section 9. The tag is not a number to add but a value to **assign**, so two rules change compared with p010:

- applying a tag **replaces** the node's sum (`v * length`) and **replaces** any older tag: the newer assignment wins;
- "no tag" must be different from every legal value: `None`, tested with `is not None`.

```python
class AssignSum:
    """Range assign, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.s = [0] * (4 * self.n)
        self.tag = [None] * (4 * self.n)       # None means "no pending assignment"
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
        self.s[node] = v * (hi - lo)           # the assignment REPLACES the sum
        self.tag[node] = v                     # and replaces any older pending tag

    def _push(self, node, lo, hi):
        if self.tag[node] is not None:         # "is not None": an assignment of 0 is real
            mid = (lo + hi) // 2
            self._apply(2 * node, lo, mid, self.tag[node])
            self._apply(2 * node + 1, mid, hi, self.tag[node])
            self.tag[node] = None

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
```

The starter differs in exactly one idea: it uses `0` as "no tag" and tests `if self.tag[node]:`. Then `assign(0, 8, 0)` puts a tag `0` on the root, the next partial update or query does not push it, and the children keep their old values.

## Complexity

`O(log n)` per operation, `O(n)` build, two lists of `4n`.

## Another way

With both range add and range assign (chapter section 9, "Add and assign together"), the tag becomes "assign `x` (or nothing), then add `d`", with the composition rules: a new assign wipes everything; a new add merges into a pending assign (`x + e`) or into the pending add.
