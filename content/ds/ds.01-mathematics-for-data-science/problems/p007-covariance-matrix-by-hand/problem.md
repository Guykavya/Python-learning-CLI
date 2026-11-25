# Covariance matrix by hand

Chapter section 2.4. For data `X` with `n` rows (samples) and `d` columns (features), the **covariance matrix** is `Xc^T Xc / (n - 1)` where `Xc` is `X` with each column's mean subtracted. Entry `[i][j]` says how feature `i` and feature `j` move together; the diagonal holds the variances.

Write `cov_matrix(X)` returning the `d x d` matrix. Do **not** call `np.cov` (the test turns it off).

## Example

```text
X = [[1, 2], [2, 4], [3, 6]]
cov_matrix(X) -> [[1, 2], [2, 4]]
```
The second feature is exactly twice the first, so every number is a multiple of the variance 1.
