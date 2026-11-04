## Approach

Binary search on the answer `k`. The check `hours(k) <= h` is monotone in `k` (a faster Koko never needs more hours), costs O(n), and the range is `[1, max(piles)]`.

## Code

```python
n, h = map(int, input().split())
piles = [int(x) for x in input().split()]
lo, hi = 1, max(piles)
while lo < hi:
    mid = (lo + hi) // 2
    hours = sum((p + mid - 1) // mid for p in piles)
    if hours <= h:
        hi = mid
    else:
        lo = mid + 1
print(lo)
```

## Complexity

O(n log(max pile)) time, O(1) extra space. For 10^5 piles up to 10^9 that is about 3 million operations.

## Another way

Start from the lower bound `ceil(sum / h)` (she cannot be faster than the total divided by the hours) to shrink the range a little: `lo = max(1, ceil(sum(piles) / h))`. The loop is the same.
