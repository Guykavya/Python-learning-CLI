## Approach

Add a column called `const` full of ones to the predictors, then fit.

## Code

```python
import statsmodels.api as sm


def fit_ols(df, y, xs):
    X = sm.add_constant(df[xs])
    return sm.OLS(df[y], X).fit()
```

## Complexity

O(n p^2) for the fit.

## Another way

The formula interface adds the intercept for you: `smf.ols("y ~ x1 + x2", data=df).fit()`; use `- 1` or `+ 0` to remove it on purpose.
