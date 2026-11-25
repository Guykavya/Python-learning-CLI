import numpy as np


def simple_fit(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xm, ym = x.mean(), y.mean()
    sxx = float(np.sum((x - xm) ** 2))
    if sxx == 0:
        raise ValueError("x has no spread")
    slope = float(np.sum((x - xm) * (y - ym)) / sxx)
    return float(ym - slope * xm), slope
