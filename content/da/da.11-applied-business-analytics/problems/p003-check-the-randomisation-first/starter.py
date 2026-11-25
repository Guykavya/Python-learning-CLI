import numpy as np
from scipy import stats


def srm_check(counts, expected_share=(0.5, 0.5)):
    """(chi2, p) of the observed group counts against the planned shares."""
    raise NotImplementedError


def srm_verdict(counts, expected_share=(0.5, 0.5)):
    """'MISMATCH' when p < 0.001, otherwise 'ok'."""
    raise NotImplementedError
