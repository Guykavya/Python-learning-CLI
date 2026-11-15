## Approach

Follow the half-open loop: `a[mid] < x` moves `lo` to `mid + 1`, anything else moves `hi` to `mid`.

## Expected output

```text
x = 2
  lo 0 mid 4 hi 8 a[mid] 5
  lo 0 mid 2 hi 4 a[mid] 2
  lo 0 mid 1 hi 2 a[mid] 2
  lo 0 mid 0 hi 1 a[mid] 1
  answer 1
x = 7
  lo 0 mid 4 hi 8 a[mid] 5
  lo 5 mid 6 hi 8 a[mid] 7
  lo 5 mid 5 hi 6 a[mid] 7
  answer 5
x = 8
  lo 0 mid 4 hi 8 a[mid] 5
  lo 5 mid 6 hi 8 a[mid] 7
  lo 7 mid 7 hi 8 a[mid] 9
  answer 7
```

## Why

For x = 2, when `mid = 2` and `a[mid] = 2`, the test `a[mid] < 2` is False, so `hi = mid`: the loop keeps searching to the **left** of a hit, because an earlier 2 might exist. That is how it finds the first 2.
The answer for x is always the number of elements smaller than x: 1 element is smaller than 2, and 5 are smaller than 7 (1, 2, 2, 2, 5).
For x = 8, `lo` ends at 7 and `a[7] = 9`, the first value `>= 8`. It is not equal to 8, so "found" needs the extra check `lo < n and a[lo] == x`.
