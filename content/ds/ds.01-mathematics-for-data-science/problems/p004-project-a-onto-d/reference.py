import numpy as np


def project(a, d):
    a = np.asarray(a, dtype=float)
    d = np.asarray(d, dtype=float)
    dd = float(d @ d)
    if dd == 0:
        raise ValueError("cannot project onto the zero vector")
    return (float(a @ d) / dd) * d
