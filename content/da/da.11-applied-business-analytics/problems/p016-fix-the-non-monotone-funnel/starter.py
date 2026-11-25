import numpy as np
import pandas as pd


def funnel_table(df, steps):
    """Counts each step column on its own (BUG: a step can exceed the one before it)."""
    n = len(df)
    rows = [("sessions", n, np.nan, 100.0)]
    prev = n
    for s in steps:
        k = int(df[s].sum())
        rows.append((s, k, k / prev * 100 if prev else np.nan, k / n * 100))
        prev = k
    t = pd.DataFrame(rows, columns=["step", "sessions", "% of previous step", "% of all sessions"])
    t["dropped"] = t["sessions"].shift(1) - t["sessions"]
    return t, 0
