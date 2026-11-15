## Approach

Apply the slope test at every `mid`: rising means the peak is to the right (`lo = mid + 1`), falling means the peak is at `mid` or to its left (`hi = mid`).

## Expected output

```text
lo 0 mid 3 hi 6 12 > 9 go left
lo 0 mid 1 hi 3 3 < 8 go right
lo 2 mid 2 hi 3 8 < 12 go right
peak index 3 value 12
```

## Why

Step 1: `mid = 3`, `a[3] = 12 > 9 = a[4]`: falling, so the peak is at 3 or to the left, `hi = 3`.
Step 2: `lo = 0, hi = 3, mid = 1`: `3 < 8`: rising, `lo = 2`.
Step 3: `lo = 2, hi = 3, mid = 2`: `8 < 12`: rising, `lo = 3`. Now `lo == hi = 3`: the peak 12.
`hi = mid` is needed because `mid` itself may be the peak. `mid + 1` is safe because `mid < hi` inside the loop, so `mid + 1 <= hi`. At the end the range holds one index, and by the invariant "the peak is inside `[lo, hi]`" it is the peak.
