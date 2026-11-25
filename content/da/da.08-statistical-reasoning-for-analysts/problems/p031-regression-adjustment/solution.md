## Approach

Including the confounders in the model removes their influence from the app coefficient, provided they are the confounders that matter and are measured. Here both are in the table, so the adjusted estimate lands near the truth, with an honest interval.

## Code

```python
import statsmodels.formula.api as smf


def adjusted_effect(df):
    d = df.assign(app_i=df["app"].astype(int))
    fit = smf.ols("spend ~ app_i + engagement + income", data=d).fit()
    lo, hi = fit.conf_int().loc["app_i"]
    return float(fit.params["app_i"]), float(lo), float(hi)
```

## Complexity

O(n x p^2) for p predictors.

## Another way

With hidden confounders (the chapter's income in section 10) the same code gives a wrong answer with a confident interval: adjustment only removes what you measured. A randomised experiment is the clean fix.
