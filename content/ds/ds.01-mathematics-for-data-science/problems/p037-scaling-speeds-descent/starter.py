import numpy as np


def steps_to_converge(X, y, lr, tol, max_steps=100_000):
    """Number of gradient-descent steps until |gradient| < tol (max_steps if it never happens)."""
    raise NotImplementedError
