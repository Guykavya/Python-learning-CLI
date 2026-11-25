import statsmodels.formula.api as smf


def adjusted_effect(df):
    d = df.assign(app_i=df["app"].astype(int))
    fit = smf.ols("spend ~ app_i + engagement + income", data=d).fit()
    lo, hi = fit.conf_int().loc["app_i"]
    return float(fit.params["app_i"]), float(lo), float(hi)
