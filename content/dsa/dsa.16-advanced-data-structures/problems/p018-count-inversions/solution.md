## Approach

Chapter section 12. Scan left to right. The inversions that end at `x` are the earlier elements strictly greater than `x`: all `seen` earlier elements minus those `<= x`. A Fenwick tree over **ranks** counts the earlier elements per value, so "those `<= x`" is a prefix sum.

```python
class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open; 1-indexed inside."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        """Sum of a[0:r]."""
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total


def count_inversions(a):
    ranks = {v: i for i, v in enumerate(sorted(set(a)))}     # coordinate compression
    bit = Fenwick(len(ranks))                                 # how many earlier elements have each rank
    inversions = 0
    for seen, x in enumerate(a):                              # seen = number of earlier elements
        k = ranks[x]
        inversions += seen - bit.prefix(k + 1)                # earlier elements strictly greater than x
        bit.add(k, 1)
    return inversions
```

Trace on `[40, 10, 30, 10, 20]` (ranks `10:0, 20:1, 30:2, 40:3`): the new inversions are 0, 1, 1, 2, 2, total 6. The second `10` adds 2 (the 40 and the 30), not 3: the earlier `10` is equal and does not count.

## Complexity

Sorting for the ranks `O(n log n)`, then `n` queries and updates of `O(log n)`: `O(n log n)` time, `O(n)` memory.

## Another way

Merge sort (dsa.05, section 9): while merging, every time an element of the right half is placed before the remaining `k` elements of the left half, it closes `k` inversions. Also `O(n log n)`, and in Python often faster than a Fenwick tree for `10**6` numbers because it works on whole lists.
