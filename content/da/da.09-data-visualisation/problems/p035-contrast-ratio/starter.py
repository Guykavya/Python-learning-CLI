import matplotlib.colors
import numpy as np


def rel_luminance(hex_color):
    """WCAG relative luminance (0 black .. 1 white) of a colour such as '#777777'."""
    raise NotImplementedError


def contrast_ratio(fg, bg="#ffffff"):
    """(lighter + 0.05) / (darker + 0.05)."""
    raise NotImplementedError


def passes_aa(fg, bg="#ffffff", large=False):
    """True when the contrast ratio is at least 4.5 (3 for large text and graphics)."""
    raise NotImplementedError
