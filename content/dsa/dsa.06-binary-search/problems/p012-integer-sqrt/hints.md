## Hint 1

Which values can the answer take? Name a safe lower and a safe upper limit. For `n = 10^18` do you really have to search up to `n`?

## Hint 2

The predicate `r * r <= n` is True...True False...False. You want the **last** True. Search `r` in `[0, n]`; since `sqrt(n) <= n` for `n >= 1` this is safe (a smaller `hi` such as `10^9 + 1` is faster).

## Hint 3

```
lo, hi = 0, n + 1            # answer in [lo, hi): first r with r*r > n, minus 1
while lo < hi:
    mid = (lo + hi) // 2
    if mid * mid > n: hi = mid
    else: lo = mid + 1
print(lo - 1)
```
Here `lo` ends as the first `r` with `r*r > n`.
