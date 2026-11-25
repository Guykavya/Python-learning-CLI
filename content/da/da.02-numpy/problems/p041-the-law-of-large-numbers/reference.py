import numpy as np


def running_mean_of_flips(n, rng):
    """Running proportion of heads in n coin flips made with rng."""
    flips = rng.integers(0, 2, size=n)
    return np.cumsum(flips) / np.arange(1, n + 1)
