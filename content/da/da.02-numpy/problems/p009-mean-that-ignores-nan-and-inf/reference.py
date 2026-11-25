import numpy as np


def clean_mean(x):
    x = np.asarray(x, dtype=float)
    ok = np.isfinite(x)
    n_dropped = int(x.size - np.count_nonzero(ok))
    if not ok.any():
        return float("nan"), n_dropped
    return float(x[ok].mean()), n_dropped
