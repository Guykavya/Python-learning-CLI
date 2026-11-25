import statsmodels.formula.api as smf


def adjusted_effect(df):
    """Return (coef, ci_low, ci_high) for app in spend ~ app + engagement + income (OLS, 95% CI)."""
    raise NotImplementedError
