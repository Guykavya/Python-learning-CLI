## Hint 1

Which of the five outputs come from one regression fit? What do you need besides the coefficient for the report (the standard error)? Write the verdict and the report last.

## Hint 2

```text
d = study_df.assign(app_i=study_df["app"].astype(int))
fit = smf.ols("spend ~ app_i + engagement + age + C(city)", data=d).fit(cov_type="HC3")
est = fit.params["app_i"] ; lo, hi = fit.conf_int().loc["app_i"] ; se = fit.bse["app_i"]
```
