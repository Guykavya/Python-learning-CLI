import numpy as np
import matplotlib.pyplot as plt


def bubble_sizes(values, max_area):
    """Marker areas proportional to the values; the largest gets max_area. Negative -> ValueError('negative value')."""
    raise NotImplementedError


def bubble_chart(x, y, values, max_area=400):
    """Scatter of y against x with area-proportional bubbles. Return the Figure."""
    raise NotImplementedError
