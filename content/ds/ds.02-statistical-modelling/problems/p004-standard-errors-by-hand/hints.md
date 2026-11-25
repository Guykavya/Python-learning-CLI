## Hint 1

Which two numbers do you need before you can write sigma2? Where do the fitted values come from?

## Hint 2

```text
b = solve(X'X, X'y)
resid = y - X @ b
sigma2 = sum(resid^2) / (n - p)
cov = sigma2 * inv(X'X)
return sqrt(diag(cov))
```
