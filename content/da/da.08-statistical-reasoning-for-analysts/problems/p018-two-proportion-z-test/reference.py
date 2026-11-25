import numpy as np
from scipy import stats


def two_prop_test(kA, nA, kB, nB):
    pA, pB = kA / nA, kB / nB
    p = (kA + kB) / (nA + nB)
    se = np.sqrt(p * (1 - p) * (1 / nA + 1 / nB))
    if se == 0:
        return 0.0, 1.0
    z = (pA - pB) / se
    return float(z), float(2 * stats.norm.sf(abs(z)))
