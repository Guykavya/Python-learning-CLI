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
    vifs = [variance_inflation_factor(exog, i) for i, nm in enumerate(names)]
    return {
        "r2": float(result.rsquared),
        "bp_p": float(het_breuschpagan(resid, exog)[1]),
        "dw": float(sm.stats.durbin_watson(result.fittedvalues)),
        "n_high_leverage": int(np.sum(lev > p / n)),
        "n_cooks_flagged": int(np.sum(cooks > 4 / n)),
        "max_vif": float(max(vifs)),
    }
