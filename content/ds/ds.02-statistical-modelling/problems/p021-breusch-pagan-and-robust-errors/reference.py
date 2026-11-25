import numpy as np
from statsmodels.stats.diagnostic import het_breuschpagan


def hetero_check(result):
    lm, lm_p, f, f_p = het_breuschpagan(result.resid, result.model.exog)
    robust = result.get_robustcov_results(cov_type="HC3")
    return {
        "bp_p": float(lm_p),
        "se_ordinary": np.asarray(result.bse),
        "se_robust": np.asarray(robust.bse),
    }
