import numpy as np
from scipy import stats


def wilson(k, n, level=0.95):
    if n < 1 or not 0 <= k <= n:
        raise ValueError("need n >= 1 and 0 <= k <= n")
    z = stats.norm.ppf((1 + level) / 2)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(max(0.0, centre - half)), float(min(1.0, centre + half))
