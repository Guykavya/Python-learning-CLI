## Approach

Chapter section 10. Everything follows from `add` and `prefix`:

- `range_sum(l, r) = prefix(r) - prefix(l)` (the first `r` elements minus the first `l`);
- `get(i)` is a range of length one; `set(i, v)` adds the difference `v - get(i)`;
- the constructor fills `t` in `O(n)`: copy the values, then push each completed cell `k` into its parent `k + lowbit(k)` exactly once.

```python
class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n, a=None):
        self.n = n
        self.t = [0] * (n + 1)              # t[0] is never used
        if a is not None:                   # O(n) build: push each cell into its parent once
            for k in range(1, n + 1):
                self.t[k] += a[k - 1]
                parent = k + (k & -k)
                if parent <= n:
                    self.t[parent] += self.t[k]

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

    def range_sum(self, l, r):
        """Sum of a[l:r]."""
        return self.prefix(r) - self.prefix(l)

    def get(self, i):
        """a[i]"""
        return self.range_sum(i, i + 1)

    def set(self, i, v):
        """a[i] = v"""
        self.add(i, v - self.get(i))
```

Why the build works: cell `k` covers `(k - lowbit(k), k]`, and its pieces are cells with smaller indices that have `k` as their parent. Processing `k` in increasing order, all of them were pushed into `t[k]` before we reach it, so it is complete when we push it on.

## Complexity

Build `O(n)`; every other operation `O(log n)`. Memory `n + 1`.

## Another way

An iterative sum segment tree (p006) does the same in `2n` memory; the Fenwick tree is shorter and has a smaller constant. For a list that never changes, plain prefix sums (p001) are simplest.
