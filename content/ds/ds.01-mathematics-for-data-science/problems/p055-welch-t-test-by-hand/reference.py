import math

import numpy as np


def welch_t(a, b, t_sf):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    sa = a.var(ddof=1) / len(a)
    sb = b.var(ddof=1) / len(b)
    t = (a.mean() - b.mean()) / math.sqrt(sa + sb)
    df = (sa + sb) ** 2 / (sa ** 2 / (len(a) - 1) + sb ** 2 / (len(b) - 1))
    return float(t), float(df), float(2 * t_sf(abs(t), df))
