import numpy as np


def ranks(x, descending=False):
    x = np.asarray(x)
    key = -x if descending else x
    order = np.argsort(key, kind="stable")
    result = np.empty(len(x), dtype=np.intp)
    result[order] = np.arange(len(x))
    return result
