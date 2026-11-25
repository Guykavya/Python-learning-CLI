import numpy as np


def gradient_descent(grad, w0, lr, steps):
    w = np.array(w0, dtype=float)
    history = [w.copy()]
    for _ in range(steps):
        w = w - lr * np.asarray(grad(w), dtype=float)
        history.append(w.copy())
    return w, history
