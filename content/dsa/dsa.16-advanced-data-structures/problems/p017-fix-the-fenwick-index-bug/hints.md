## Hint 1

`i & i` is just `i`, so `i += i & i` doubles `i`: from 3 it goes to 6, 12, ... and skips cell 4, which covers position 3 (1-indexed `1..4`). The step must be the **lowest set bit**, `i & -i` (chapter section 10).

## Hint 2

`prefix(r)` reads the cells `r, r - lowbit(r), ...`, which are 1-indexed: cell `k` stands for the user's `a[k - 1]`. So `add(i, v)` must start at cell `i + 1`. Starting at 0 also makes `i & -i` equal 0, and the loop never moves.

## Hint 3

```python
def add(self, i, v):
    i += 1                      # user index 0..n-1 -> cell 1..n
    while i <= self.n:
        self.t[i] += v
        i += i & -i             # the next cell that also covers this position
```
