import matplotlib
import numpy as np


def luminance_profile(name, n=64):
    """Luminance of n colours along the matplotlib colour map `name` (NumPy array)."""
    raise NotImplementedError


def is_monotone_lightness(name):
    """True when the luminance never changes direction along the map."""
    raise NotImplementedError


def pick_sequential(names):
    """The first honest (monotone) colour map name in the list, or None."""
    raise NotImplementedError
