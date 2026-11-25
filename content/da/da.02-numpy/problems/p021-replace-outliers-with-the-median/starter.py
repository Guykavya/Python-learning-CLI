import numpy as np


def cap_outliers(x, k=1.5):
    """(copy of x with values outside the k*IQR fences replaced by the median, number replaced)."""
    # TODO
    return np.asarray(x, dtype=float).copy(), 0
