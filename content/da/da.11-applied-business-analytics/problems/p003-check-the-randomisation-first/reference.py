import numpy as np
from scipy import stats


def srm_check(counts, expected_share=(0.5, 0.5)):
    share = np.asarray(expected_share, float)
    if abs(share.sum() - 1) > 1e-9:
        raise ValueError("shares must add up to 1")
    counts = np.asarray(counts, float)
    chi2, p = stats.chisquare(counts, counts.sum() * share)
    return float(chi2), float(p)


def srm_verdict(counts, expected_share=(0.5, 0.5)):
    return "MISMATCH" if srm_check(counts, expected_share)[1] < 0.001 else "ok"
