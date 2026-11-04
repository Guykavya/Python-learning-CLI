## Hint 1

If a substring of length 5 occurs twice, what about length 4? What does that tell you about searching for the answer?

## Hint 2

Binary search on `k` between 0 and `n - 1`. `repeats(k)` rolls a hash over windows of length `k` and returns True as soon as a hash is seen twice.

## Hint 3

```
lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi + 1) // 2
    if repeats(mid): lo = mid
    else: hi = mid - 1
print(lo)
```
