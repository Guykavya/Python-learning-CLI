import numpy as np  # patsy looks up `np` here, in the file that calls ols()
import statsmodels.formula.api as smf


def fit_wages(df):
    formula = ("np.log(wage) ~ experience"
               " + C(education, Treatment(reference='school'))"
               " + C(city)")
    return smf.ols(formula, data=df).fit()
