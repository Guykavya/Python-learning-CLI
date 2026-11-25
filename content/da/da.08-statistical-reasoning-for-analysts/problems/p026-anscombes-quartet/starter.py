import numpy as np


def pair_summary(x, y):
    """Return (mean_x, mean_y, var_x (ddof=1), r, slope, intercept)."""
    raise NotImplementedError


def looks_linear(x, y):
    """True when no curvature (<50% RSS gain from x^2), max leverage < 0.5 and max|r| / median|r| < 5."""
    raise NotImplementedError
