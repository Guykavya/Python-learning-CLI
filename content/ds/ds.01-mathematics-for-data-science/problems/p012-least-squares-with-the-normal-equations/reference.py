import numpy as np


def least_squares(A, b):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.linalg.solve(A.T @ A, A.T @ b)
