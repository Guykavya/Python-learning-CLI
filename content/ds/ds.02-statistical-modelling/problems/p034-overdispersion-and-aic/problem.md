# Overdispersion and AIC

Chapter sections 15.3 and 16. A Poisson model assumes the variance of a count equals its mean. Real counts often vary more (**overdispersion**). Two tools:

- the **dispersion ratio**: Pearson chi-squared divided by the residual degrees of freedom of the Poisson fit; about 1 is fine, well above 1 is a warning;
- **AIC** (smaller is better) to compare the Poisson model with a negative-binomial model, which has an extra parameter for the extra variance.

Write two functions.

**`choose_count_model(df)`**, with columns `y` (counts) and `x` (a numeric predictor). Fit `y ~ x`:

1. a Poisson GLM (`smf.glm`, family `Poisson`); the dispersion ratio is its `pearson_chi2 / df_resid`
2. a negative-binomial model (`smf.negativebinomial("y ~ x", data=df)`, which estimates the extra parameter), fitted with `disp=0`; ignore its convergence warnings

and return `{"dispersion": ratio, "aic_poisson": ..., "aic_negbin": ..., "best": "poisson" or "negbin"}` where `best` is the name of the model with the lower AIC. Take the Poisson AIC from `smf.poisson("y ~ x", data=df).fit(disp=0).aic` so both AICs use the same likelihood definition.

**`lr_test(big, small)`** for two nested fitted likelihood models (for example two `smf.poisson` fits): return `(lr, df, p)` where `lr = 2 * (big.llf - small.llf)`, `df = big.df_model - small.df_model` and `p` is the upper tail of the chi-squared distribution with `df` degrees of freedom at `lr` (`scipy.stats.chi2.sf`).

## Example

```text
overdispersed data: choose_count_model(df) -> {"dispersion": 2.2, "aic_poisson": 3172.8, "aic_negbin": 2865.1, "best": "negbin"}
Poisson data:       choose_count_model(df) -> {"dispersion": 1.0, "aic_poisson": 2502.8, "aic_negbin": 2504.8, "best": "poisson"}
```
