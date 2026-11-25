import numpy as np
import pandas as pd


def pooled_retention(active, sizes, ks):
    out = {}
    for k in ks:
        if k not in active.columns:
            out[k] = np.nan
            continue
        col = active[k]
        ok = col.notna()
        out[k] = float(col[ok].sum() / sizes[ok].sum()) if ok.any() else np.nan
    return pd.Series(out, dtype=float)
