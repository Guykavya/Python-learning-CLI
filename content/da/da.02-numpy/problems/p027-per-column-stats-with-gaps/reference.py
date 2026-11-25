import numpy as np


def column_stats(x):
    """Dict with 'count', 'mean', 'std' per column, nan ignored, no RuntimeWarning."""
    x = np.asarray(x, dtype=float)
    valid = ~np.isnan(x)
    count = valid.sum(axis=0)
    has_data = count > 0
    total = np.where(valid, x, 0.0).sum(axis=0)
    mean = np.divide(total, count, out=np.full(x.shape[1], np.nan), where=has_data)
    dev = np.where(valid, x - mean, 0.0)
    var = np.divide((dev ** 2).sum(axis=0), count, out=np.full(x.shape[1], np.nan), where=has_data)
    return {"count": count, "mean": mean, "std": np.sqrt(var)}
