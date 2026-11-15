## Hint 1

What is the smallest possible answer and what is the largest? Think of `m = n` (every element alone) and `m = 1` (one piece).

## Hint 2

Search `S` in `[max(a), sum(a)]`. `pieces(S)` is non-increasing in `S`, so "`pieces(S) <= m`" is False...False True...True. Find the first True.

## Hint 3

```
lo, hi = max(a), sum(a)
while lo < hi:
    mid = (lo + hi) // 2
    if pieces(mid) <= m: hi = mid
    else: lo = mid + 1
print(lo)
```
`pieces(S)`: `count = 1; cur = 0; for x in a: if cur + x > S: count += 1; cur = 0; cur += x`.
