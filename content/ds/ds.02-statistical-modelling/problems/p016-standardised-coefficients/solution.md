## Approach

Standardise all the columns involved (response and predictors), fit with an intercept (it will come out as 0 up to rounding), and return the slopes.

## Code

```python
import pandas as pd
import statsmodels.api as sm


def standardised_coefs(df, y, xs):
    cols = [y] + list(xs)
    z = (df[cols] - df[cols].mean()) / df[cols].std()
    res = sm.OLS(z[y], sm.add_constant(z[list(xs)])).fit()
    return res.params.drop("const")
```

## Complexity

O(n p^2).

## Another way

Fit once on the raw data and compute `b * sd(x) / sd(y)`. Same numbers, no second fit.
