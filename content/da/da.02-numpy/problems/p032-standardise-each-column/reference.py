import numpy as np


def zscore(x, axis=0, ddof=0):
    """Standardise along axis; constant slices give 0."""
    x = np.asarray(x, dtype=float)
    mean = x.mean(axis=axis, keepdims=True)
    std = x.std(axis=axis, ddof=ddof, keepdims=True)
    return (x - mean) / np.where(std == 0, 1.0, std)
