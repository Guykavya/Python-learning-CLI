# Anscombe's quartet

Chapter section 7. Four data sets with **identical summary statistics** and four completely different pictures. A summary can hide
curvature, outliers and leverage points.

Write two functions for 1-D lists or arrays `x`, `y` of the same length (n >= 3, `x` not constant, else `ValueError`):

1. `pair_summary(x, y)` returns the tuple `(mean_x, mean_y, var_x, r, slope, intercept)`: variance with `ddof=1`, `r` Pearson, and
   `slope`, `intercept` of the least-squares line (`np.polyfit(x, y, 1)`).
2. `looks_linear(x, y)` returns `True` only when a straight line is a **trustworthy** description. Fit the line and the quadratic
   `y ~ 1 + x + x^2` (`np.linalg.lstsq`), compute the residuals `r` of the line, and return `True` when **all three** hold:
   - the quadratic reduces the residual sum of squares by **less than 50%** (no curvature);
   - the largest leverage `max(diag(H))`, with `H = A (A'A)^-1 A'` and `A = [1, x]`, is **below 0.5** (no single point decides the line);
   - `max|r| / median|r|` is **below 5** (no outlier).

The four sets (the published numbers, `x` shared by the first three):

```python
X = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
Y1 = [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]
Y2 = [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]
Y3 = [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]
X4 = [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8]
Y4 = [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]
```

## Example

`pair_summary(X, Y1)` is about `(9.0, 7.5, 11.0, 0.816, 0.5, 3.0)`: so is every other set. `looks_linear` is `True` only for set 1: set 2 is a curve, set 3 has
an outlier, set 4 is decided by a single point.
