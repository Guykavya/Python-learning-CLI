## Hint 1

Which capacities can be the answer at all? Give a smallest and a largest possible value. (Think of the heaviest package, and of shipping everything on one day.)

## Hint 2

Search `C` in `[max(w), sum(w)]`. Write a helper `days_needed(C)`: it scans the weights once, adds each package to the current load, and starts a new day when the load would exceed `C`. Then `ok(C) = days_needed(C) <= D`.

## Hint 3

```
lo, hi = max(w), sum(w)
while lo < hi:
    mid = (lo + hi) // 2
    if days_needed(mid) <= D: hi = mid
    else: lo = mid + 1
print(lo)
```
Inside `days_needed`: `days = 1; load = 0; for x in w: if load + x > C: days += 1; load = 0; load += x`.
