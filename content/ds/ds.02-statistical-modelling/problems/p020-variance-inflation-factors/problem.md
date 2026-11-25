# Variance inflation factors

Chapter section 9.4. The **variance inflation factor** of a predictor says how much its coefficient's variance is inflated because the other predictors can already predict it:

```text
VIF_j = 1 / (1 - R2_j)
```

where `R2_j` is the R-squared of a regression of predictor `j` on **all the other predictors** (with an intercept). A VIF above about 10 is a warning.

Write `vif_table(df, predictors)`. It returns a `pandas.Series` indexed by predictor name with each VIF, **sorted from largest to smallest**. Compute `R2_j` yourself with `sm.OLS`; do not call `variance_inflation_factor`.

## Example

```text
df: x1, x2 = x1 + tiny noise, x3 independent
vif_table(df, ["x1", "x2", "x3"])
-> x1 ~ 1000, x2 ~ 1000, x3 ~ 1
```
