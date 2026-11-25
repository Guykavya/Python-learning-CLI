# Lasso zeros out junk

Chapter section 8. The lasso penalty can set coefficients to exactly zero, so it works as a feature selector.

Write `lasso_selected(X, y, alpha)`. `X` is a DataFrame. Standardise the columns with `StandardScaler`, fit `Lasso(alpha=alpha)` on the standardised data and return the **names of the columns whose coefficient is not exactly zero**, as a list in the original column order. For `alpha < 0` raise `ValueError`.

## Example

```text
10 columns x0..x9; the target uses only x0, x1, x2 (coefficients 3, 2, -2) plus noise
lasso_selected(X, y, alpha=0.3)   ->  ["x0", "x1", "x2"]
lasso_selected(X, y, alpha=10)    ->  []                      # too much penalty: nothing survives
```
