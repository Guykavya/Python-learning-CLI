# Fit a line with `lstsq`

Chapter section 16.6. Write `fit_line(x, y)` that fits `y ≈ slope * x + intercept` by least squares with `np.linalg.lstsq` and returns the tuple `(slope, intercept)` as two Python `float`s.

- Build the design matrix: a column of `x` and a column of ones, shape `(n, 2)`.
- Raise `ValueError` when:
  - `x` and `y` have different lengths, or fewer than 2 points are given;
  - all `x` values are equal ("vertical" data): no single line `y = a x + b` fits best, and the matrix has rank 1. Use the `rank` that `lstsq` returns to detect it.
- Lists or arrays; integers allowed. Do not change the inputs.

## Example

(Output measured with NumPy 2.5.4; the last digits of rounding errors can differ on another machine.)

```python
fit_line([0, 1, 2, 3], [1, 3, 5, 7])
# (1.9999999999999998, 1.0)
#   slope 2 and intercept 1 up to rounding: the points lie exactly on y = 2x + 1
fit_line([1, 2, 3], [2, 2, 5])
# (1.4999999999999996, 1.978993310921642e-16)
#   slope 1.5 and intercept 0 up to rounding; np.polyfit([1, 2, 3], [2, 2, 5], 1) agrees
fit_line([4, 4, 4], [1, 2, 3])
# ValueError: all x values are equal (rank 1): a vertical line cannot be written as y = slope * x + intercept
```
