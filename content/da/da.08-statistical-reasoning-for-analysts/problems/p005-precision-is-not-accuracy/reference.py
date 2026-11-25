import numpy as np


def bias_spread_rmse(estimates, truth):
    e = np.asarray(estimates, dtype=float)
    bias = e.mean() - truth
    sd = e.std()
    rmse = np.sqrt(np.mean((e - truth) ** 2))
    return float(bias), float(sd), float(rmse)
