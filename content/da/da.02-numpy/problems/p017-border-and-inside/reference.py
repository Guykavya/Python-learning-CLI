import numpy as np


def border_values(a):
    h, w = a.shape
    if h == 1:
        return a[0, :].copy()
    if w == 1:
        return a[:, 0].copy()
    top = a[0, :]
    right = a[1:, -1]
    bottom = a[-1, -2::-1]
    left = a[-2:0:-1, 0]
    return np.concatenate([top, right, bottom, left])


def interior(a):
    return a[1:-1, 1:-1]
