## Hint 1

Why centre the columns before solving? What happens to the intercept equation when `X` and `y` are centred?

## Hint 2

```text
xm = X.mean(axis=0); ym = y.mean(); Xc = X - xm; yc = y - ym
beta = solve(Xc.T @ Xc + alpha * eye(p), Xc.T @ yc)
intercept = ym - xm @ beta
```
