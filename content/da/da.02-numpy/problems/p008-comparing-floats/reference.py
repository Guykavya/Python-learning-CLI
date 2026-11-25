import numpy as np


def close_mask(a, b, rtol=1e-05, atol=1e-08):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.abs(a - b) <= atol + rtol * np.abs(b)
