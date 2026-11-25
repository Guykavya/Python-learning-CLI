## Hint 1

What does the formula need for the treatment column (a number, not a Boolean)? Which method of the fitted model gives the coefficient and which gives its interval?

## Hint 2

```text
fit = smf.ols("spend ~ app_i + engagement + income", data=df.assign(app_i=df["app"].astype(int))).fit()
coef = fit.params["app_i"] ; lo, hi = fit.conf_int().loc["app_i"]
```
