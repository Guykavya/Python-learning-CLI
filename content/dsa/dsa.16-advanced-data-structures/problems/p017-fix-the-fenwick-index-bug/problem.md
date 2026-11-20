# Fix the Fenwick index bug

A colleague wrote this Fenwick tree for a stock-keeping tool. Its public interface is meant to be **0-indexed and half-open** (`add(i, v)` is `a[i] += v`; `range_sum(l, r)` is the sum of `a[l:r]`). Sometimes the program hangs forever, and sometimes the totals are wrong.

```python
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        while i <= self.n:
            self.t[i] += v
            i += i & i

    def prefix(self, r):
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l)
```

The code is in `starter.py`. Find **both** bugs in `add`, write one sentence about each in a comment above `add`, and fix them. Do not change the interface.

## Example (after the fix)

```python
>>> fw = Fenwick(5)
>>> fw.add(0, 7)              # before the fix: hangs forever
>>> fw.add(2, 5)
>>> fw.range_sum(0, 5), fw.range_sum(1, 3), fw.range_sum(0, 1)
(12, 5, 7)
```

## Think about

1. What is `0 & 0`? What does the loop do with `i = 0`?
2. What is `i & i`, and what is `i & -i`? Write the update path of 1-indexed 3 for both.
3. Which cell must hold the user's `a[0]`, given that `prefix(r)` reads cells `1..r`?
