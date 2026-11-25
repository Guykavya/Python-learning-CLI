import numpy as np


def seasonal_naive(train, horizon, season=7):
    t = np.asarray(train, dtype=float)
    if len(t) < season:
        raise ValueError("need at least one full season of history")
    last = t[-season:]
    return np.array([last[i % season] for i in range(horizon)])
