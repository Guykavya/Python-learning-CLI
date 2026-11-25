import matplotlib.colors
import numpy as np


def rel_luminance(hex_color):
    rgb = np.array(matplotlib.colors.to_rgb(hex_color))
    lin = np.where(rgb <= 0.03928, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return float(lin @ np.array([0.2126, 0.7152, 0.0722]))


def contrast_ratio(fg, bg="#ffffff"):
    a, b = rel_luminance(fg), rel_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def passes_aa(fg, bg="#ffffff", large=False):
    return bool(contrast_ratio(fg, bg) >= (3.0 if large else 4.5))
