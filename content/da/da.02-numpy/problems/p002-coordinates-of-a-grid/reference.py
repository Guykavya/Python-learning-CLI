import numpy as np


def grid_coordinates(h, w):
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    return ys, xs
