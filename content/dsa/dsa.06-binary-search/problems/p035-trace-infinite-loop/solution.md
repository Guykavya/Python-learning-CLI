## Approach

Trace with the faulty update `lo = mid`. Compare the range before and after each step: a correct loop always makes it smaller.

## Expected output

```text
step 1 mid 1 lo 1 hi 3
step 2 mid 2 lo 2 hi 3
step 3 mid 2 lo 2 hi 3
step 4 mid 2 lo 2 hi 3
step 5 mid 2 lo 2 hi 3
step 6 mid 2 lo 2 hi 3
stopped: lo 2 hi 3 steps 6
```

## Why

Step 1: `lo = 0, hi = 3`, `mid = 1`, `a[1] = 3 < 7`, `lo = 1`. Step 2: `mid = (1 + 3) // 2 = 2`, `a[2] = 5 < 7`, `lo = 2`.
Step 3: `lo = 2, hi = 3`, `mid = (2 + 3) // 2 = 2`. `a[2] < 7` again, `lo = mid = 2`: **nothing changed**. The same state repeats in steps 4, 5, 6, and it would repeat forever.
It is stuck whenever `hi == lo + 1` and the test is True, because `(lo + hi) // 2 = lo`. Fixes: use `lo = mid + 1` (the usual one), or round the midpoint up, `mid = (lo + hi + 1) // 2`, when the other branch is `hi = mid - 1`.
