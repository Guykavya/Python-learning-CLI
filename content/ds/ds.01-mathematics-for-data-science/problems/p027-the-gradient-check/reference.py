import numpy as np


def grad_check(f, grad, p, h=1e-5):
    p = np.asarray(p, dtype=float)
    a = np.asarray(grad(p), dtype=float)
    num = np.zeros_like(p)
    for i in range(len(p)):
        step = np.zeros_like(p)
        step[i] = h
        num[i] = (f(p + step) - f(p - step)) / (2 * h)
    denom = np.linalg.norm(a) + np.linalg.norm(num)
    if denom == 0:
        return 0.0
    return float(np.linalg.norm(a - num) / max(denom, 1e-12))
