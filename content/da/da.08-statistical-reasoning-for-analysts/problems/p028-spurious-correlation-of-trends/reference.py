import numpy as np


def diff_corr(a, b):
    da, db = np.diff(np.asarray(a, float)), np.diff(np.asarray(b, float))
    if len(da) != len(db) or len(da) < 2:
        raise ValueError("need two series of the same length, at least 3 points")
    if da.std() == 0 or db.std() == 0:
        raise ValueError("r is undefined when one variable does not vary")
    return float(np.corrcoef(da, db)[0, 1])
