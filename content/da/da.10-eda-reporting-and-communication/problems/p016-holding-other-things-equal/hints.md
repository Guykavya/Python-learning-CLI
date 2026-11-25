## Hint 1

Two numbers come from two different calculations. For the naive one you only need four counts. For the adjusted one, which columns go into `X`, and where in the fitted result do you find the coefficient and its interval?

## Hint 2

```text
X = sm.add_constant(df[["late", "new"]].astype(float))
fit = sm.GLM(df["churn"].astype(float), X, family=sm.families.Binomial()).fit()
odds_ratio = exp(fit.params["late"]); ci = exp(fit.conf_int().loc["late"])
naive: a = churners among late, b = stayers among late, c, d for not late -> (a/b) / (c/d)
```
