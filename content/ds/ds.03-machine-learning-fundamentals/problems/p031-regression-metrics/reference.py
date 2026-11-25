import math

import numpy as np


def reg_metrics(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    if y.shape != p.shape:
        raise ValueError("y and p must have the same length")
    if np.any(y == 0):
        raise ValueError("MAPE is undefined when a target is 0")
    tss = float(np.sum((y - y.mean()) ** 2))
    if tss == 0:
        raise ValueError("R2 is undefined for a constant target")
    e = y - p
    return {
        "MAE": float(np.mean(np.abs(e))),
        "RMSE": float(math.sqrt(np.mean(e ** 2))),
        "R2": float(1 - np.sum(e ** 2) / tss),
        "MAPE": float(np.mean(np.abs(e / y))),
    }
