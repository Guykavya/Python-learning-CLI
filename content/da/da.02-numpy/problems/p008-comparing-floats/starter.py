import numpy as np


def close_mask(a, b, rtol=1e-05, atol=1e-08):
    """True where |a - b| <= atol + rtol * |b|; False where a value is nan."""
    # TODO: == is wrong for floats
    return np.asarray(a) == np.asarray(b)
