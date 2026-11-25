## Approach

This is the whole module in one function: clean on a rule you can defend, fit a log-log model, read the elasticity with its interval, run the diagnostics, check the error on rows the model has not seen, and report unusual rows instead of deleting them silently.

## Code

```python
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

FORMULA = ("np.log(price_lakh) ~ np.log(area_sqft / 1000) + bedrooms + bathrooms"
           " + age_years + C(locality) + parking")
AREA = "np.log(area_sqft / 1000)"


def house_study(df):
    clean = df[df["area_sqft"] <= 4000]
    res = smf.ols(FORMULA, data=clean).fit()
    exog = res.model.exog
    names = list(res.model.exog_names)
    vifs = [variance_inflation_factor(exog, i) for i, nm in enumerate(names) if nm != "Intercept"]

    n = len(clean)
    idx = np.random.default_rng(0).permutation(n)
    cut = int(n * 0.75)
    train, test = clean.iloc[idx[:cut]], clean.iloc[idx[cut:]]
    fit_tr = smf.ols(FORMULA, data=train).fit()
    err = np.log(test["price_lakh"]) - fit_tr.predict(test)
    stud = res.get_influence().resid_studentized_external
    lo, hi = res.conf_int().loc[AREA]
    return {
        "n_dropped": int(len(df) - n),
        "n_used": int(n),
        "elasticity": float(res.params[AREA]),
        "elasticity_ci": (float(lo), float(hi)),
        "max_vif": float(max(vifs)),
        "bp_p": float(het_breuschpagan(res.resid, exog)[1]),
        "holdout_rmse": float(np.sqrt(np.mean(err ** 2))),
        "outliers": sorted(int(i) for i in clean.index[np.abs(stud) > 3]),
    }
```

## Complexity

Two OLS fits and about p auxiliary regressions for the VIFs.

## Another way

Fit with and without the impossible row and show how much the elasticity moves: with the bad row left in, the interval often misses the true 0.85, which is exactly why the cleaning step is part of the study.
