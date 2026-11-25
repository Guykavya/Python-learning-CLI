import numpy as np


def bar_values(ax):
    """[(label, value)] for each bar: heights for vertical bars, widths for horizontal bars."""
    raise NotImplementedError


def line_data(ax, i=0):
    """(x, y) arrays of the i-th line on the Axes; y as floats."""
    raise NotImplementedError
