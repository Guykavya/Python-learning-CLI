import warnings

import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats


def choose_count_model(df):
    """{'dispersion', 'aic_poisson', 'aic_negbin', 'best'} for y ~ x."""
    raise NotImplementedError


def lr_test(big, small):
    """(lr, df, p) likelihood-ratio test of two nested fits."""
    raise NotImplementedError
