## Hint 1

Look at `a[mid]` and the last element `a[hi]`. If `a[mid] > a[hi]`, where must the "drop" (the minimum) be: left or right of `mid`?

## Hint 2

If `a[mid] > a[hi]`, the drop is somewhere in `mid + 1 .. hi`, so `lo = mid + 1`. Otherwise `a[mid] <= a[hi]` means `mid .. hi` is sorted, so the minimum is at `mid` or to its left: `hi = mid`. Use `while lo < hi`; at the end `lo` is the index of the minimum.

## Hint 3

```
lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if ask(mid) > ask(hi): lo = mid + 1
    else: hi = mid
print("!", ask(lo))
```
Why compare with `a[hi]` and not with `a[lo]`? With `a[lo]` a sorted array and a rotated array look alike on the left side.
