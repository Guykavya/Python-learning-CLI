## Hint 1

Look at `a[lo]` and `a[mid]`. If `a[lo] <= a[mid]`, which half has no rotation point inside it?

## Hint 2

If `a[lo] <= a[mid]` the left half `lo..mid` is sorted. The target is inside it exactly when `a[lo] <= x < a[mid]` (the case `x == a[mid]` was already handled). Then `hi = mid - 1`, otherwise `lo = mid + 1`. In the other case the right half is sorted: the target is inside when `a[mid] < x <= a[hi]`.

## Hint 3

```
while lo <= hi:
    mid = (lo + hi) // 2
    if a[mid] == x: return mid
    if a[lo] <= a[mid]:                      # left half sorted
        if a[lo] <= x < a[mid]: hi = mid - 1
        else: lo = mid + 1
    else:                                    # right half sorted
        if a[mid] < x <= a[hi]: lo = mid + 1
        else: hi = mid - 1
return -1
```
