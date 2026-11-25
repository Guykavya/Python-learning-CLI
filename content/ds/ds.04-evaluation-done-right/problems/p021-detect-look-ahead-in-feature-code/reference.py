import numpy as np


def uses_future(feature_fn, series, t):
    full = feature_fn(series).iloc[t]
    cut = feature_fn(series.iloc[: t + 1]).iloc[t]
    return bool(not np.isclose(full, cut, equal_nan=True))
