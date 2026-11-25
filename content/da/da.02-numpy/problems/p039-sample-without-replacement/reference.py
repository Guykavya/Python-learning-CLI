import numpy as np


def sample_rows(x, k, rng):
    """k different rows of x, chosen with rng; x is not changed."""
    x = np.asarray(x)
    n = len(x)
    if not 0 <= k <= n:
        raise ValueError(f"cannot pick k={k} different rows from n={n}")
    idx = rng.choice(n, size=k, replace=False)
    return x[idx]
