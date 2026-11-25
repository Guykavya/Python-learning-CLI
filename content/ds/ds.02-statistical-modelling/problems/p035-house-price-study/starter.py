import numpy as np
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor


def house_study(df):
    """Clean, fit the log-log house-price model, run diagnostics and a hold-out check."""
    raise NotImplementedError
