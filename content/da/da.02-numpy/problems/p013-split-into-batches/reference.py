import numpy as np


def batches(x, size):
    if size <= 0:
        raise ValueError(f"size must be positive, got {size}")
    return [x[start:start + size] for start in range(0, len(x), size)]
