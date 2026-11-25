import numpy as np


def count_by_index(idx, n):
    """How many times each position 0..n-1 appears in idx."""
    counts = np.zeros(n, dtype=np.int64)
    counts[idx] += 1          # TODO: this is the trap
    return counts


def add_amounts(totals, idx, amounts):
    """New array: totals plus amounts[i] added at idx[i], duplicates accumulated."""
    out = totals.copy()
    out[idx] += amounts       # TODO: this is the trap
    return out
