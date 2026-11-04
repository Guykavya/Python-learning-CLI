## Hint 1

Compare with the lower bound from the previous problem. Which single character in the comparison changes when the equal elements should be counted on the left side?

## Hint 2

Now the predicate is "`a[i] > x`" and you want its first True. If `a[mid] <= x`, then `mid` is on the left side: `lo = mid + 1`. Otherwise `hi = mid`.

## Hint 3

```
lo, hi = 0, n
while lo < hi:
    mid = (lo + hi) // 2
    if a[mid] <= x: lo = mid + 1
    else: hi = mid
print(lo)
```
