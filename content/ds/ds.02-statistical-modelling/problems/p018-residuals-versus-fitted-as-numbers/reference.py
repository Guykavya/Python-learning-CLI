import numpy as np


def funnel_ratio(result):
    fitted = np.asarray(result.fittedvalues)
    resid = np.asarray(result.resid)
    lo, hi = np.quantile(fitted, [1 / 3, 2 / 3])
    top = resid[fitted >= hi]
    bottom = resid[fitted <= lo]
    return float(np.std(top, ddof=1) / np.std(bottom, ddof=1))
