## Approach

Trace the two loops separately. Both halve the range, but they define "range" differently: `[lo, hi]` against `[lo, hi)`.

## Expected output

```text
9 closed ([3, 5, 4], 4) half-open ([3, 5, 4], 4)
10 closed ([3, 5, 4], -1) half-open ([3, 5, 4], 5)
1 closed ([3, 1, 0], 0) half-open ([3, 1, 0], 0)
14 closed ([3, 5, 6], -1) half-open ([3, 5, 6], 7)
```

## Why

Both loops probe the same indices here because the list has 7 elements and `(0 + 6) // 2 = (0 + 7) // 2 = 3`; the ranges differ by one end but the middle lands on the same spot for this size.
The closed version answers "where is it, or -1". The half-open version always runs until `lo == hi` and returns the **first index with `a[i] >= x`**: for 10 that is index 5 (value 11), for 14 it is 7 (past the end).
The half-open version never stops early, so it may probe once more, but it gives one answer that works for found and not-found alike: "where would x go".
