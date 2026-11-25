from itertools import combinations

import matplotlib.colors
import numpy as np

DEUTAN = np.array([[0.625, 0.375, 0.0], [0.700, 0.300, 0.0], [0.0, 0.300, 0.700]])


def simulate(hex_color):
    return np.clip(DEUTAN @ np.array(matplotlib.colors.to_rgb(hex_color)), 0, 1)


def separation(c1, c2, simulated=True):
    a = simulate(c1) if simulated else np.array(matplotlib.colors.to_rgb(c1))
    b = simulate(c2) if simulated else np.array(matplotlib.colors.to_rgb(c2))
    return float(np.linalg.norm(a - b))


def safe_pairs(palette, min_sep):
    """All pairs (palette[i], palette[j]), i < j, whose simulated separation is at least min_sep."""
    raise NotImplementedError
