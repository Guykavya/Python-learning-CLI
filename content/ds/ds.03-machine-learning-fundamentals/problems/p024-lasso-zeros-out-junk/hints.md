## Hint 1

Which attribute of a fitted `Lasso` holds the coefficients? How do you turn 'non-zero' into the names of columns?

## Hint 2

```text
Z = StandardScaler().fit_transform(X)
coef = Lasso(alpha=alpha).fit(Z, y).coef_
return [name for name, c in zip(X.columns, coef) if c != 0]
```
