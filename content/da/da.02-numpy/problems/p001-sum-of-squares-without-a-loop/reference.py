import numpy as np


def sum_squares(n):
    values = np.arange(n, dtype=np.int64)
    return int((values * values).sum())
