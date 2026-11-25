import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


def mean_ci(x, level=0.95):
    x = np.asarray(x, float)
    se = x.std(ddof=1) / np.sqrt(len(x))
    h = stats.t.ppf((1 + level) / 2, len(x) - 1) * se
    return x.mean(), h


def means_with_ci(df, group, value):
    """One errorbar point per group (sorted): the mean with its 95% half-width; y from 0; title with '95% CI'. Return the Figure."""
    raise NotImplementedError
