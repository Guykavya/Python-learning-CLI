import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def omitted_bias(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 1, n)
    hours = 0.8 * ability + rng.normal(0, 1, n)
    score = 50 + 2 * hours + 5 * ability + rng.normal(0, 3, n)
    df = pd.DataFrame({"ability": ability, "hours": hours, "score": score})
    long = smf.ols("score ~ hours + ability", data=df).fit()
    short = smf.ols("score ~ hours", data=df).fit()
    delta = np.cov(df["ability"], df["hours"])[0, 1] / df["hours"].var()
    return {
        "long_slope": float(long.params["hours"]),
        "short_slope": float(short.params["hours"]),
        "predicted_short": float(long.params["hours"] + long.params["ability"] * delta),
    }
