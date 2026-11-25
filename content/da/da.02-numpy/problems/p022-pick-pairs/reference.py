import numpy as np


def pick(matrix, rows, cols):
    return matrix[np.asarray(rows), np.asarray(cols)]


def diagonal_of_top(matrix, k):
    idx = np.arange(k)
    return matrix[idx, idx]
