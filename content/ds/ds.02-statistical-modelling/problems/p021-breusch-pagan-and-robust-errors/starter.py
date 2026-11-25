import numpy as np
from statsmodels.stats.diagnostic import het_breuschpagan


def hetero_check(result):
    """{'bp_p', 'se_ordinary', 'se_robust'} for a fitted OLS result."""
    raise NotImplementedError
