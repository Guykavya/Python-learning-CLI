## Hint 1

Write the running totals of `[2, 4, 6, 8]` with a `0` in front: `[0, 2, 6, 12, 20]`. The sum of the window `x[1:3]` (4 + 6 = 10) is the difference of which two running totals?

## Hint 2

If `c` has `n + 1` running totals (starting with 0), the sum of the window that starts at `i` is `c[i + k] - c[i]`. Which two slices of `c` give all of these differences at once?

## Hint 3

```text
x = float array
if not 1 <= k <= len(x): raise ValueError(f"... k={k} ... len(x)={len(x)}")
c = cumsum(insert(x, 0, 0.0))        # n + 1 values
return (c[k:] - c[:-k]) / k          # n - k + 1 values
```
