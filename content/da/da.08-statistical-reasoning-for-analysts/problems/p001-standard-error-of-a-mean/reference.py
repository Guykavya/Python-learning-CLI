import numpy as np


def standard_error(x):
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        raise ValueError("one value has no spread")
    return float(x.std(ddof=1) / np.sqrt(len(x)))
