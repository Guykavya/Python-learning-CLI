import pandas as pd
import statsmodels.api as sm


def standardised_coefs(df, y, xs):
    cols = [y] + list(xs)
    z = (df[cols] - df[cols].mean()) / df[cols].std()
    res = sm.OLS(z[y], sm.add_constant(z[list(xs)])).fit()
    return res.params.drop("const")
