import numpy as np


def normalise(x):
    """Rescale x to the range [0, 1]: the minimum becomes 0 and the maximum 1."""
    x = np.asarray(x)
    lo = x.min()
    span = x.max() - lo
    if span == 0:
        return np.zeros(x.shape)
    return (x - lo) / span
