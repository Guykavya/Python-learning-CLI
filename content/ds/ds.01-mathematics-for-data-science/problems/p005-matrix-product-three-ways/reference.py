import numpy as np


def matmul(A, B):
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    m, n = A.shape
    n2, p = B.shape
    if n != n2:
        raise ValueError(f"shapes {A.shape} and {B.shape} do not fit")
    C = np.zeros((m, p))
    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]
    return C
