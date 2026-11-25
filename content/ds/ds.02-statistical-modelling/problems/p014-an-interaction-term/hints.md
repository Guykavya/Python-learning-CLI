## Hint 1

In `a * b` the formula contains `a`, `b` and `a:b`. What does the coefficient of `a` mean once `a:b` is in the model?

## Hint 2

```text
res = ols(formula).fit()
base = res.params["experience"]
slopes = {"school": base}
for level in ["degree", "masters"]:
    slopes[level] = base + res.params["experience:C(...)[T.level]"]
```
Look at `res.params.index` to see the exact name of an interaction term.
