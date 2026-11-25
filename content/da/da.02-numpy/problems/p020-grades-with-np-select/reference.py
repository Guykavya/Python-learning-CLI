import numpy as np


def grades(scores):
    s = np.asarray(scores, dtype=float)
    return np.select(
        [np.isnan(s), s >= 90, s >= 75, s >= 60, s >= 40],
        ["missing", "A", "B", "C", "D"],
        default="F",
    )
