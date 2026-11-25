import numpy as np
from scipy import stats


def power(p0, p1, n, sims, rng):
    ka = rng.binomial(n, p0, sims)
    kb = rng.binomial(n, p1, sims)
    pp = (ka + kb) / (2 * n)
    se = np.sqrt(pp * (1 - pp) * (2 / n))
    z = np.divide((kb - ka) / n, se, out=np.zeros(sims), where=se > 0)
    return float(np.mean(2 * stats.norm.sf(np.abs(z)) < 0.05))
