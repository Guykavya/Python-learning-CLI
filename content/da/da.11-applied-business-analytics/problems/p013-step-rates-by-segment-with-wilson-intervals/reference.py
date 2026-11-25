import numpy as np
import pandas as pd
from scipy import stats


def step_rates(df, by, steps):
    rows = []
    for key, g in df.groupby(by):
        prev = len(g)
        for s in steps:
            k = int(g[s].sum())
            if prev == 0:
                rate = lo = hi = np.nan
            else:
                ci = stats.binomtest(k, prev).proportion_ci(0.95, method="wilson")
                rate, lo, hi = k / prev * 100, ci.low * 100, ci.high * 100
            rows.append({by: key, "step": s, "n_prev": prev, "n": k, "rate %": rate, "CI low": lo, "CI high": hi})
            prev = k
    return pd.DataFrame(rows, columns=[by, "step", "n_prev", "n", "rate %", "CI low", "CI high"])
