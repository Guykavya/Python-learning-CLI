import numpy as np


def count_by_index(idx, n):
    return np.bincount(idx, minlength=n)


def add_amounts(totals, idx, amounts):
    out = totals.copy()
    np.add.at(out, idx, amounts)
    return out
