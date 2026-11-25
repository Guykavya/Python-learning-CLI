## Hint 1

Which rows go to `fit`, and which rows do you pass to `predict`? Why must the RMSE for the test rows use `result.predict(test_df)` and not the fitted values?

## Hint 2

```text
idx = permutation(n); cut = int(n * (1 - test_frac))
train, test = df.iloc[idx[:cut]], df.iloc[idx[cut:]]
res = ols(formula, train).fit()
rmse(d) = sqrt(mean((d["y"] - res.predict(d)) ** 2))
```
