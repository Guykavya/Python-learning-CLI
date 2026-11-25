import numpy as np


def cap_outliers(x, k=1.5):
    x = np.asarray(x, dtype=float)
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    outside = (x < low) | (x > high)
    cleaned = np.where(outside, np.median(x), x)
    return cleaned, int(np.count_nonzero(outside))
