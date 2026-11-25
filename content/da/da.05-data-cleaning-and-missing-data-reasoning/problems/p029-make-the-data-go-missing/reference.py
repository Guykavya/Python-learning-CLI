import numpy as np
import pandas as pd


def simulate_missing(pop, mechanism, rate, rng):
    out = pop.copy()
    n = len(out)
    if mechanism == "MCAR":
        w = np.ones(n)
    elif mechanism == "MAR":
        w = np.where(out["age"] < 40, 2.0, 1.0)
    elif mechanism == "MNAR":
        w = np.where(out["income"] > out["income"].median(), 5.0, 1.0)
    else:
        raise ValueError(f"unknown mechanism {mechanism!r}")
    p = np.clip(rate * w / w.mean(), 0, 1)
    hide = rng.random(n) < p
    out.loc[hide, "income"] = np.nan
    return out
