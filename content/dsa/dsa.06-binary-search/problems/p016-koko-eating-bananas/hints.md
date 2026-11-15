## Hint 1

What is the smallest and the largest speed that can possibly be the answer? Why is it never useful to go faster than the biggest pile?

## Hint 2

The answer lies in `[1, max(piles)]`. Define `ok(k)`: "all piles can be finished in at most `h` hours at speed `k`". It is False...False True...True. Search for the first True.

## Hint 3

```
lo, hi = 1, max(piles)
while lo < hi:
    mid = (lo + hi) // 2
    hours = sum((p + mid - 1) // mid for p in piles)
    if hours <= h: hi = mid
    else: lo = mid + 1
print(lo)
```
