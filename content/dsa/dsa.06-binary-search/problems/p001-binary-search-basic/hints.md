## Hint 1

What does the range `lo..hi` mean? After one comparison with `a[mid]`, which half of the list can you throw away, and why is `mid` itself thrown away too?

## Hint 2

If `a[mid] < target`, the target (if present) lies strictly to the right of `mid`, so the new `lo` is `mid + 1`. If `a[mid] > target`, the new `hi` is `mid - 1`. When the range is empty (`lo > hi`) the target is not there.

## Hint 3

```
lo, hi = 0, n - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if a[mid] == x: answer = mid; stop
    elif a[mid] < x: lo = mid + 1
    else: hi = mid - 1
if not stopped: answer = -1
```
Do the search again for every query, but read the input only once.
