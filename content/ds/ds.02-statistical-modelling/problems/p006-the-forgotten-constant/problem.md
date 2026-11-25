# The forgotten constant

Chapter section 4. `sm.OLS(y, X)` fits a line through the **origin** unless `X` contains a column of ones. Forgetting this is the most common statsmodels mistake: the fit still runs, and the numbers look plausible but are wrong.

Write `fit_ols(df, y, xs)`: `df` is a DataFrame, `y` the name of the response column, `xs` a list of predictor column names. Return the fitted statsmodels results object of an OLS model **with an intercept**.

## Example

```text
res = fit_ols(df, "price", ["area"])
res.params          # index: ['const', 'area']
res.exog_names      # ['const', 'area']
```
