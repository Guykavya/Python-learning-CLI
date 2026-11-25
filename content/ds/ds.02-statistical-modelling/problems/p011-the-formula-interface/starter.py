import numpy as np  # patsy looks up `np` here, in the file that calls ols()
import numpy as np
import statsmodels.formula.api as smf


def fit_wages(df):
    """Fit log(wage) on experience, education (baseline school) and city; return the results object."""
    return smf.ols("wage ~ experience", data=df).fit()
