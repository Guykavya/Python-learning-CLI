## Hint 1

First decide when the answer is impossible. Then think: which values can the answer take? You only need to try days that actually appear in the list (or any value between its minimum and maximum).

## Hint 2

Search the day in `[min(bloom), max(bloom)]`. `bouquets(d)` counts runs of `k` adjacent flowers with `bloom <= d`. The predicate `bouquets(d) >= m` is False...False True...True. Find the first True.

## Hint 3

```
if m * k > n: print(-1)
else:
    lo, hi = min(bloom), max(bloom)
    while lo < hi:
        mid = (lo + hi) // 2
        if bouquets(mid) >= m: hi = mid
        else: lo = mid + 1
    print(lo)
```
In `bouquets(d)`: `run = 0; count = 0; for b in bloom: if b <= d: run += 1; if run == k: count += 1; run = 0; else: run = 0`.
