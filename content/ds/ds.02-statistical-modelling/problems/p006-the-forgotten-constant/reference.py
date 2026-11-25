import statsmodels.api as sm


def fit_ols(df, y, xs):
    X = sm.add_constant(df[xs])
    return sm.OLS(df[y], X).fit()
