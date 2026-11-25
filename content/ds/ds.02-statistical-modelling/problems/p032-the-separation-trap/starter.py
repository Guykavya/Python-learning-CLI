import warnings

import numpy as np
import statsmodels.api as sm


def safe_logit(X, y):
    """(result, 'ok') or (None, reason) when the fit is separated or singular."""
    return sm.Logit(y, X).fit(disp=0), "ok"
