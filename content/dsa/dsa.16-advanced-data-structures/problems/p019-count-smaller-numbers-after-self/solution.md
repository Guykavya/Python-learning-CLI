## Approach

The mirror image of p018 (chapter section 12, "Variants"): scan from the **right**, so the tree holds exactly the later numbers; count those with a strictly smaller rank, then insert the current one.

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


def smaller_after(nums):
    ranks = {v: i for i, v in enumerate(sorted(set(nums)))}
    bit = Fenwick(len(ranks))
    out = [0] * len(nums)
    for i in range(len(nums) - 1, -1, -1):        # from the right: the tree holds the later numbers
        k = ranks[nums[i]]
        out[i] = bit.prefix(k)                    # later numbers with a strictly smaller rank
        bit.add(k, 1)
    return out
```

`sum(smaller_after(a))` equals the number of inversions of `a` (p018): each inversion `i < j, a[i] > a[j]` is counted once, at `i`.

## Complexity

`O(n log n)` time (compression plus `n` tree operations), `O(n)` memory.

## Another way

Merge sort that carries the original indices: when an element of the left half is placed, it adds the number of right-half elements already placed (all smaller) to its own counter. Or keep a sorted list of the later numbers and use `bisect_left` plus `insort`: `O(n)` per insertion in theory, but fast in CPython for 10**5 numbers because the list shifting is done in C.
