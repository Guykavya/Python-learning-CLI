## Hint 1

The first occurrence is at `lower_bound(x)` if that index holds `x`. Where is the last one, relative to `upper_bound(x)`?

## Hint 2

Last = `upper_bound(x) - 1`. The value is present exactly when `lower_bound(x) < n` and `a[lower_bound(x)] == x`. If it is missing, print `-1 -1`.

## Hint 3

```
lo = first index with a[i] >= x
if lo == n or a[lo] != x: print(-1, -1)
else:
    hi = first index with a[i] > x
    print(lo, hi - 1)
```
