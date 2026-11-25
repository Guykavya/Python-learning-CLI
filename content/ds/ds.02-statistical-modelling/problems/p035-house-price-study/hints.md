## Hint 1

Do the steps in order and keep the cleaned DataFrame. Which of the numbers in the table come from one fit, and which need another fit on a split?

## Hint 2

```text
clean = df[df.area_sqft <= 4000]
res = ols(formula, clean).fit()
elasticity = res.params["np.log(area_sqft / 1000)"]  # look at res.params.index for the exact name
vif: loop over exog columns except the intercept
bp: het_breuschpagan(res.resid, res.model.exog)[1]
holdout: permutation(n) -> fit on first 75%, rmse on last 25%
outliers: index labels where |resid_studentized_external| > 3
```
