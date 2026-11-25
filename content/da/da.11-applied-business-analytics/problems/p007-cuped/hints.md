## Hint 1

`np.cov(y, x)[0, 1]` is the sample covariance (`ddof=1` by default), so divide it by `np.var(x, ddof=1)`. Why subtract `x - mean(x)` and not `x`?

## Hint 2

```text
yv, xv = float arrays
theta = np.cov(yv, xv)[0, 1] / np.var(xv, ddof=1)
adjusted = yv - theta * (xv - xv.mean())
r2 = np.corrcoef(yv, xv)[0, 1] ** 2
```
