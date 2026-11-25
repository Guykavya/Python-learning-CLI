import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf


def rate_model(df):
    """{'rate_ratio', 'ci_low', 'ci_high'} of treated vs untreated, with log(exposure) as the offset."""
    raise NotImplementedError
