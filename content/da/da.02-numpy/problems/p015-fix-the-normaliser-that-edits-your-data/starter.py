import numpy as np


def normalise(x):
    """Rescale x to the range [0, 1]: the minimum becomes 0 and the maximum 1."""
    x -= x.min()
    x /= x.max()
    return x
