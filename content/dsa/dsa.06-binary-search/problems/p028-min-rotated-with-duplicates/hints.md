## Hint 1

Compare `a[mid]` with `a[hi]`. There are three outcomes: greater, smaller, equal. The first two behave as in the distinct case. What can you say in the equal case about `a[hi]`?

## Hint 2

If `a[mid] == a[hi]`, then `a[hi]` is not needed to remember anything the copy at `mid` does not already tell: dropping it (`hi -= 1`) cannot lose the minimum, because a copy of the same value stays at `mid` (and `mid < hi`).

## Hint 3

```
while lo < hi:
    mid = (lo + hi) // 2
    if a[mid] > a[hi]: lo = mid + 1
    elif a[mid] < a[hi]: hi = mid
    else: hi -= 1
print(a[lo])
```
