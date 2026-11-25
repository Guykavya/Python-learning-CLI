## Approach

The naive odds ratio compares late with not-late weeks, but those groups differ in how many new customers they contain. The model compares late with not-late **within the same value of `new`**, so the confounder no longer leaks into the estimate.

## Code

```python
import numpy as np
import statsmodels.api as sm


def late_effect(df):
    X = sm.add_constant(df[["late", "new"]].astype(float))
    fit = sm.GLM(df["churn"].astype(float), X, family=sm.families.Binomial()).fit()
    lo, hi = fit.conf_int().loc["late"]
    late = df["late"] == 1
    churn = df["churn"] == 1
    a, b = (late & churn).sum(), (late & ~churn).sum()
    c, d = (~late & churn).sum(), (~late & ~churn).sum()
    return {"odds_ratio": float(np.exp(fit.params["late"])), "ci_low": float(np.exp(lo)), "ci_high": float(np.exp(hi)),
            "naive_odds_ratio": float((a / b) / (c / d))}
```

## Complexity

A few iterations of the fitting algorithm, each O(n).

## Another way

`smf.logit("churn ~ late + new", data=df).fit(disp=0)` gives the same coefficients with a formula. Stratifying by `new` (an odds ratio in each stratum, then a Mantel-Haenszel average) gives a similar answer without a model.
