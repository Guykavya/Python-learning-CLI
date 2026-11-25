import numpy as np


def r_squared(y, fitted, p):
    y = np.asarray(y, dtype=float)
    fitted = np.asarray(fitted, dtype=float)
    n = len(y)
    rss = float(np.sum((y - fitted) ** 2))
    tss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - rss / tss
    adj = 1 - (1 - r2) * (n - 1) / (n - p - 1)
    return r2, adj
