import numpy as np


def compress(M, tol=0.05):
    M = np.asarray(M, dtype=float)
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    total = float(np.sqrt((s ** 2).sum()))
    r = len(s)
    k = r
    for j in range(1, r + 1):
        err = float(np.sqrt((s[j:] ** 2).sum())) / total
        if err < tol:
            k = j
            break
    approx = (U[:, :k] * s[:k]) @ Vt[:k]
    return approx, k, k * (M.shape[0] + M.shape[1] + 1)
