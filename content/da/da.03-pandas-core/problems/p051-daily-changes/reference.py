import numpy as np
import pandas as pd


def daily_changes(s):
    return pd.DataFrame({
        "diff": s.diff(),
        "pct_change": s.pct_change().replace([np.inf, -np.inf], np.nan),
        "running_total": s.cumsum(),
    })
