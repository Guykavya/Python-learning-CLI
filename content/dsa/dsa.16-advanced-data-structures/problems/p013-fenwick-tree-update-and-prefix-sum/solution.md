## Approach

Chapter section 10. Cell `t[k]` stores the sum of the `lowbit(k)` positions ending at `k` (1-indexed). Those blocks are nested or disjoint, so

- a **prefix** `1..r` is tiled by `t[r]`, `t[r - lowbit(r)]`, ...: clear the lowest bit each step;
- the cells **containing** position `k` are `t[k]`, `t[k + lowbit(k)]`, ...: add the lowest bit each step.

```python
class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)              # t[0] is never used

    def add(self, i, v):
        """a[i] += v"""
        i += 1                              # to 1-indexed
        while i <= self.n:
            self.t[i] += v
            i += i & -i                     # the next cell that covers position i

    def prefix(self, r):
        """Sum of a[0:r]."""
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r                     # drop the lowest set bit
        return total
```

The 1-indexing is hidden: `add` shifts `i` to `i + 1`; `prefix(r)` needs no shift, because the first `r` elements end at 1-indexed position `r`. Check the example: `add(3, 94)` touches 1-indexed `4 -> 8`, so only `t[4]` and `t[8]` change.

## Complexity

`O(log n)` per operation: each loop step clears or carries one bit. Memory `n + 1` numbers.

## Another way

Build from a list in `O(n)` instead of `n` calls to `add`: copy `a` into `t[1..n]`, then for `k = 1..n` add `t[k]` into its parent `t[k + lowbit(k)]` (if `<= n`). Chapter section 10, "The linear-time build".
