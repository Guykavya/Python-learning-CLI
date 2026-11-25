import numpy as np
import statsmodels.api as sm


def late_effect(df):
    X = sm.add_constant(df[["late", "new"]].astype(float))
    fit = sm.GLM(df["churn"].astype(float), X, family=sm.families.Binomial()).fit()
    lo, hi = fit.conf_int().loc["late"]
    late = df["late"] == 1
    churn = df["churn"] == 1
    a, b = (late & churn).sum(), (late & ~churn).sum()
    c, d = (~late & churn).sum(), (~late & ~churn).sum()
    return {"odds_ratio": float(np.exp(fit.params["late"])), "ci_low": float(np.exp(lo)), "ci_high": float(np.exp(hi)),
            "naive_odds_ratio": float((a / b) / (c / d))}
