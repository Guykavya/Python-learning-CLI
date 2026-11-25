import math

import numpy as np


def mean_ci(x, level, t_ppf):
    x = np.asarray(x, dtype=float)
    n = len(x)
    se = x.std(ddof=1) / math.sqrt(n)
    t = t_ppf(0.5 + level / 2, n - 1)
    return float(x.mean() - t * se), float(x.mean() + t * se)
