## Hint 1

You know the sum of the window `a[0..2]`. The next window is `a[1..3]`. Which element left and which one entered?

## Hint 2

Sum the first `k` elements once. Then for `r` from `k` to `n - 1`: add `a[r]`, subtract `a[r - k]`, and compare with
the best so far. Start `best` at the first window's sum, not at 0: every sum can be negative.

## Hint 3

```
s = sum(a[0:k]); best = s
for r in k .. n-1:
    s += a[r] - a[r - k]
    best = max(best, s)
print best
```
