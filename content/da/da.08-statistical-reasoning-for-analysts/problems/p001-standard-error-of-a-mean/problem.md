# Standard error of a mean

Chapter section 2. A sample mean changes from sample to sample. How much it typically changes is the **standard error**
(SE): the sample standard deviation divided by the square root of the sample size,

`SE = s / sqrt(n)`, where `s` uses `ddof=1` (divide by n - 1).

Write `standard_error(x)` for a list or NumPy array `x` of numbers. It returns the SE as a float.

- one value has no spread, so n = 1 raises `ValueError` with the text `one value has no spread`;
- constant data have `s = 0`, so the SE is 0.

```python
standard_error([2, 4, 6, 8])      # s = 2.582, n = 4  ->  1.2910
```

## Example

For `[10, 12]`: `s = 1.4142`, `n = 2`, so the SE is `1.4142 / 1.4142 = 1.0`.
