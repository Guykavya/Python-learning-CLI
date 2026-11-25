## Approach

Measure the dispersion with the Poisson fit, compare the two likelihood-based models by AIC, and implement the likelihood-ratio test as the statistic `2 * (llf_big - llf_small)` compared with a chi-squared distribution.

## Code

```python
import warnings

import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats


def choose_count_model(df):
    pois_glm = smf.glm("y ~ x", data=df, family=sm.families.Poisson()).fit()
    dispersion = float(pois_glm.pearson_chi2 / pois_glm.df_resid)
    aic_p = float(smf.poisson("y ~ x", data=df).fit(disp=0).aic)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        aic_nb = float(smf.negativebinomial("y ~ x", data=df).fit(disp=0).aic)
    return {"dispersion": dispersion, "aic_poisson": aic_p, "aic_negbin": aic_nb,
            "best": "poisson" if aic_p <= aic_nb else "negbin"}


def lr_test(big, small):
    lr = 2 * (big.llf - small.llf)
    df = big.df_model - small.df_model
    return float(lr), float(df), float(stats.chi2.sf(lr, df))
```

## Complexity

A few likelihood fits, each O(n p^2) per iteration.

## Another way

Keep Poisson but use robust or quasi-Poisson standard errors (scale the standard errors by `sqrt(dispersion)`); that fixes the intervals without changing the mean model.
