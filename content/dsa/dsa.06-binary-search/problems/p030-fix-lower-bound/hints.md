## Hint 1

Try the starter on `[2, 2, 2]` with `x = 2`, then on `[1, 2, 3]` with `x = 9`. Which of your two outputs is wrong, and what should it be?

## Hint 2

Bug 1 is in the comparison: for the lower bound the left side is the elements **strictly smaller** than `x`. Bug 2 is in the initial range: the answer `n` ("not found") must be possible, but the half-open range `[lo, hi)` can only return values `lo..hi`.

## Hint 3

```
lo, hi = 0, n          # not n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if a[mid] < x:     # not <=
        lo = mid + 1
    else:
        hi = mid
```
