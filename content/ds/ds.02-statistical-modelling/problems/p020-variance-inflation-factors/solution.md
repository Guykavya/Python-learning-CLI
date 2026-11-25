## Approach

One auxiliary regression per predictor. A predictor that the others reproduce almost perfectly has `R2` near 1, so its VIF explodes.

## Code

```python
import pandas as pd
import statsmodels.api as sm


def vif_table(df, predictors):
    vifs = {}
    for name in predictors:
        others = [p for p in predictors if p != name]
        if not others:
            vifs[name] = 1.0
            continue
        r2 = sm.OLS(df[name], sm.add_constant(df[others])).fit().rsquared
        vifs[name] = 1.0 / (1.0 - r2)
    return pd.Series(vifs).sort_values(ascending=False)
```

## Complexity

`p` regressions of O(n p^2) each.

## Another way

`statsmodels.stats.outliers_influence.variance_inflation_factor(X, i)` (the chapter's helper) computes the same numbers; use it to check yours. Remember to include the constant column in the matrix you give it.
