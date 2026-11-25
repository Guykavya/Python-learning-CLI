import numpy as np


def row_shares(x):
    x = np.asarray(x, dtype=float)
    totals = x.sum(axis=1, keepdims=True)
    out = np.zeros(x.shape)
    np.divide(x, totals, out=out, where=totals != 0)
    return out
