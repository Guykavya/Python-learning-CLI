import numpy as np
import pandas as pd


def store_growth(monthly):
    """Sorted copy with growth_pct per store (NaN for first month and after a zero month)."""
    out = monthly.sort_values(["store_id", "month"], ignore_index=True)
    growth = out.groupby("store_id")["revenue"].pct_change() * 100
    out["growth_pct"] = growth.replace([np.inf, -np.inf], np.nan)
    return out
