# The normal equations

Chapter section 3.5. For a design matrix `X` (a first column of ones for the intercept, then one column per predictor) the least-squares coefficients satisfy

```text
(X^T X) b = X^T y
```

Write `ols_coefs(X, y)` that returns the coefficient vector `b` as a 1-D NumPy array by solving this linear system with `np.linalg.solve`. `X` already contains the column of ones. Do not use `lstsq`, `polyfit` or statsmodels.

## Example

```text
X = [[1, 1], [1, 2], [1, 3], [1, 4]]
y = [2, 3, 5, 6]
ols_coefs(X, y)   ->  array([0.5, 1.4])
```
