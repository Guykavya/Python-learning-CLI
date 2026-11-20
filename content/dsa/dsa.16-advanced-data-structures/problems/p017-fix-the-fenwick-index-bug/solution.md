## Approach

Two independent bugs, both in `add`:

1. **The index shift is missing.** `prefix(r)` reads 1-indexed cells, so the user's `a[i]` lives in cell `i + 1`. Without the shift, `add(0, v)` starts at cell 0: `0 & 0 == 0`, `i` never changes, and the loop runs forever. For other indices the value lands one cell too low.
2. **`i & i` instead of `i & -i`.** `i & i` is `i`, so the loop doubles `i` (3 → 6 → 12) and skips cell 4, which covers 1-indexed position 3. The correct step is the lowest set bit (chapter section 10), which visits exactly the cells that contain the position (3 → 4 → 8 → 16).

```python
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    # Bug 1: the user's index is 0-based but the cells are 1-based, so add must start at i + 1;
    #        with i = 0 the step 0 & 0 (or 0 & -0) is 0 and the loop never ends.
    # Bug 2: i & i is i itself, so the loop doubled i and skipped cells that cover the position;
    #        the step to the next covering cell is the lowest set bit, i & -i.
    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l)
```

## Complexity

`O(log n)` per operation after the fix.

## Another way

Make the whole class 1-indexed (users pass 1-based positions) and document it. That avoids the shift, but mixes two conventions in a program that uses Python lists everywhere else; hiding the shift inside `add` keeps the interface consistent with `a[l:r]`.
