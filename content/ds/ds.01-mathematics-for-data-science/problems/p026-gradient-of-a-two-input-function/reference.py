import numpy as np


def grad_f(p):
    x, y = float(p[0]), float(p[1])
    return np.array([2 * x * y, x ** 2 + 3])
