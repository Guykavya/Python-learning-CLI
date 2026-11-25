import numpy as np


def skewness(x):
    x = np.asarray(x, dtype=float)
    d = x - x.mean()
    m2 = np.mean(d ** 2)
    if m2 == 0:
        return 0.0
    return float(np.mean(d ** 3) / m2 ** 1.5)


def excess_kurtosis(x):
    x = np.asarray(x, dtype=float)
    d = x - x.mean()
    m2 = np.mean(d ** 2)
    if m2 == 0:
        return 0.0
    return float(np.mean(d ** 4) / m2 ** 2 - 3.0)
