## Hint 1

Which times are certainly too small and which are certainly big enough? Give a lower and an upper limit. (Think of using only the fastest machine.)

## Hint 2

The fastest machine alone needs `min(k) * t` seconds, so that is a valid upper limit. Search `T` in `[1, min(k) * t]`: `made(T) >= t` is False...False True...True. Find the first True.

## Hint 3

```
lo, hi = 1, min(k) * t
while lo < hi:
    mid = (lo + hi) // 2
    if sum(mid // x for x in k) >= t: hi = mid
    else: lo = mid + 1
print(lo)
```
