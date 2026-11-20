## Approach

Chapter section 15. Precompute the minimum of every block whose length is a power of two. Any range `[l, r)` is covered by two such blocks of the largest length `2**k <= r - l`: one starting at `l`, one ending at `r`. They may overlap; the minimum does not care, because `min(x, x) = x` (it is **idempotent**).

```python
class SparseMin:
    """Static range minimum with O(1) queries. Half-open [l, r), l < r."""

    def __init__(self, a):
        n = len(a)
        self.lg = [0] * (n + 1)                   # lg[L] = floor(log2(L))
        for i in range(2, n + 1):
            self.lg[i] = self.lg[i // 2] + 1
        self.table = [list(a)]
        k = 1
        while (1 << k) <= n:
            prev, half = self.table[-1], 1 << (k - 1)
            self.table.append([min(prev[i], prev[i + half]) for i in range(n - (1 << k) + 1)])
            k += 1

    def query(self, l, r):
        k = self.lg[r - l]
        row = self.table[k]
        return min(row[l], row[r - (1 << k)])     # two blocks of 2**k that cover [l, r), maybe overlapping
```

`query(1, 7)`: length 6, `k = 2`; blocks `a[1:5]` (minimum `table[2][1] = 2`) and `a[3:7]` (`table[2][3] = 2`), overlapping at positions 3 and 4. The answer is 2.

## Complexity

Build `O(n log n)` time and memory; query `O(1)`. No updates: a change means rebuilding. For `n = 10**6` the table has about 20 rows of up to 10**6 entries, too big for comfort in Python; up to a few times 10**5 it is fine.

## Another way

A segment tree (p004 or p006) answers in `O(log n)` with `O(n)` memory and also allows updates. The sparse table wins only when the data is static and queries are very many.
