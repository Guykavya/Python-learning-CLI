import numpy as np
from scipy import stats


def ci_mean(x, level=0.95):
    x = np.asarray(x, dtype=float)
    n = len(x)
    se = x.std(ddof=1) / np.sqrt(n)
    h = stats.t.ppf((1 + level) / 2, df=n - 1) * se
    return float(x.mean() - h), float(x.mean() + h)
