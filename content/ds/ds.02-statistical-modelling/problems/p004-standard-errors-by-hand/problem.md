# Standard errors by hand

Chapter section 3.6. The standard error of each coefficient comes from the diagonal of a matrix:

```text
sigma2 = RSS / (n - p)                  # p = number of columns of X (including the constant)
se     = sqrt(diag(sigma2 * inv(X^T X)))
```

Write `ols_se(X, y)` returning a 1-D NumPy array with one standard error per column of `X` (`X` already includes the column of ones). NumPy only.

Note the divisor: `n - p`, **not** `n`. The model has used `p` degrees of freedom to estimate the coefficients.

## Example

```text
X = [[1, 1], [1, 2], [1, 3], [1, 4]]     y = [2, 3, 5, 6]
ols_se(X, y)   ->  array([0.3873..., 0.1414...])
```
