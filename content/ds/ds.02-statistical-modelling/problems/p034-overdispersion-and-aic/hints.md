## Hint 1

Which statsmodels attributes hold the Pearson statistic and the residual degrees of freedom of a GLM? What does a dispersion ratio of 2 mean for the standard errors?

## Hint 2

```text
pois = smf.glm("y ~ x", df, family=Poisson()).fit()
dispersion = pois.pearson_chi2 / pois.df_resid
aic_p = smf.poisson("y ~ x", df).fit(disp=0).aic
aic_nb = smf.negativebinomial("y ~ x", df).fit(disp=0).aic
best = "poisson" if aic_p <= aic_nb else "negbin"
lr = 2 * (big.llf - small.llf); df = big.df_model - small.df_model; p = chi2.sf(lr, df)
```
