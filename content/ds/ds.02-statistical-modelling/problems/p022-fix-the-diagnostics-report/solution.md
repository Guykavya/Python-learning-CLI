## The bugs

1. `dw` used `result.fittedvalues`; Durbin-Watson is a statistic of the **residuals** (`result.resid`).
2. `n_high_leverage` used the threshold `p / n`; the rule of thumb is `2p / n`.
3. `max_vif` included the **constant** column in the loop. The VIF of the intercept column is huge and not a predictor's VIF; skip `"const"` (and `"Intercept"` for formula models).

## Fixed code

```python
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor


def diagnose(result):
    resid = np.asarray(result.resid)
    n, p = int(result.nobs), len(result.params)
    infl = result.get_influence()
    lev = infl.hat_matrix_diag
    cooks = infl.cooks_distance[0]
    exog = result.model.exog
    names = list(result.model.exog_names)
    vifs = [variance_inflation_factor(exog, i) for i, nm in enumerate(names)
            if nm not in ("const", "Intercept")]
    return {
        "r2": float(result.rsquared),
        "bp_p": float(het_breuschpagan(resid, exog)[1]),
        "dw": float(sm.stats.durbin_watson(resid)),
        "n_high_leverage": int(np.sum(lev > 2 * p / n)),
        "n_cooks_flagged": int(np.sum(cooks > 4 / n)),
        "max_vif": float(max(vifs)),
    }
```

## Another way

Break the helper into one small function per check so each can be tested alone.
