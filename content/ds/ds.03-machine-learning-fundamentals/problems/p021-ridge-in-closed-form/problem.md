# Ridge in closed form

Chapter section 8. **Ridge regression** adds a penalty `alpha * sum(beta^2)` to the squared error, which shrinks the coefficients. The intercept is **not** penalised. With centred data the solution is

```text
xm, ym   = column means of X, mean of y
beta     = solve( Xc' Xc + alpha * I , Xc' yc )       (Xc = X - xm, yc = y - ym)
intercept = ym - xm @ beta
```

Write `ridge_fit(X, y, alpha)` returning `(intercept, beta)` with `beta` a 1-D array. `X` is a NumPy array without a column of ones. A negative `alpha` raises `ValueError`. Use NumPy only.

## Example

```text
ridge_fit(X, y, alpha=0)   ->  the ordinary least-squares line
ridge_fit(X, y, alpha=100) ->  smaller coefficients, intercept close to mean(y)
```
