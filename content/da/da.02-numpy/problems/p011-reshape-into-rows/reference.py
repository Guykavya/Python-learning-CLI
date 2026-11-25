import numpy as np


def to_rows(x, k):
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    if len(x) % k != 0:
        raise ValueError(f"cannot split {len(x)} values into rows of {k}")
    return x.reshape(-1, k)
