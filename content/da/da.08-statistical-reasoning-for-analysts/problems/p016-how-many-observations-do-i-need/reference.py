import math
from scipy import stats


def _z(level):
    return stats.norm.ppf((1 + level) / 2)


def n_for_margin(sd, margin, level=0.95):
    if margin <= 0:
        raise ValueError("margin must be positive")
    return math.ceil((_z(level) * sd / margin) ** 2)


def n_for_proportion(margin, p=0.5, level=0.95):
    if margin <= 0:
        raise ValueError("margin must be positive")
    return math.ceil(_z(level) ** 2 * p * (1 - p) / margin ** 2)
