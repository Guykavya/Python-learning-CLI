import numpy as np
import pandas as pd


def adjusted_diff(df, treat, outcome, by):
    diffs, sizes, skipped = [], [], []
    for name, g in df.groupby(by):
        t = g.loc[g[treat].astype(bool), outcome]
        c = g.loc[~g[treat].astype(bool), outcome]
        if t.empty or c.empty:
            skipped.append(name)
            continue
        diffs.append(t.mean() - c.mean())
        sizes.append(len(g))
    if not diffs:
        raise ValueError("no stratum has both treated and untreated rows")
    return float(np.average(diffs, weights=sizes)), sorted(skipped)
