## Hint 1

First the residual `r = X w - y` (a vector with `n` entries). The gradient is a combination of the rows of `X` weighted by the residuals: which product gives a vector with `d` entries?

## Hint 2

```text
r = X @ w - y
return 2 / n * (X.T @ r)
```
