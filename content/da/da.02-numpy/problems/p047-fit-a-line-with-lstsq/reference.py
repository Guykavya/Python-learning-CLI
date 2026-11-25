import numpy as np


def fit_line(x, y):
    """(slope, intercept) of the least-squares line, via np.linalg.lstsq."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError(f"x and y have different lengths: {x.size} and {y.size}")
    if x.size < 2:
        raise ValueError(f"need at least 2 points, got {x.size}")
    X = np.column_stack([x, np.ones_like(x)])
    coef, residuals, rank, sing = np.linalg.lstsq(X, y, rcond=None)
    if rank < 2:
        raise ValueError(f"all x values are equal (rank {rank}): a vertical line cannot be written as y = slope * x + intercept")
    slope, intercept = coef
    return float(slope), float(intercept)
