import statsmodels.api as sm


def fit_ols(df, y, xs):
    """OLS of df[y] on df[xs] WITH an intercept; return the fitted results object."""
    return sm.OLS(df[y], df[xs]).fit()
