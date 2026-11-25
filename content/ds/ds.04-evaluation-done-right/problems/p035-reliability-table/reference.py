import numpy as np
import pandas as pd


def reliability(y, p, bins=10):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    k = np.minimum(np.floor(p * bins).astype(int), bins - 1)
    t = (pd.DataFrame({"k": k, "y": y, "p": p})
         .groupby("k")
         .agg(n=("y", "size"), predicted=("p", "mean"), observed=("y", "mean"))
         .reset_index())
    t["bin_low"] = t["k"] / bins
    return t[["bin_low", "n", "predicted", "observed"]]
