import numpy as np


def solve(A, b):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    scale = max(float(np.abs(A).max()), 1e-300)
    for c in range(n):
        piv = c + int(np.argmax(np.abs(A[c:, c])))
        if abs(A[piv, c]) < 1e-12 * scale:
            raise ValueError("singular matrix: pivot below tolerance")
        if piv != c:
            A[[c, piv]] = A[[piv, c]]
            b[[c, piv]] = b[[piv, c]]
        for r in range(c + 1, n):
            f = A[r, c] / A[c, c]
            A[r, c:] -= f * A[c, c:]
            b[r] -= f * b[c]
    x = np.zeros(n)
    for r in range(n - 1, -1, -1):
        x[r] = (b[r] - A[r, r + 1:] @ x[r + 1:]) / A[r, r]
    return x
