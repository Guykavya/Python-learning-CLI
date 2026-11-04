## Approach

The predicate `a[i] >= x` is False...False True...True on a sorted list. Search the half-open range `[lo, hi)` for the first True, with `hi = n` meaning "none found".

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
queries = [int(x) for x in input().split()]
out = []
for x in queries:
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    out.append(lo)
print("\n".join(map(str, out)))
```

## Complexity

O(q log n) time, O(1) extra space.

## Another way

Closed template with an `ans = n` variable: when `a[mid] >= x` record `ans = mid` and go left (`hi = mid - 1`), otherwise `lo = mid + 1`. Same answer, one extra variable.
