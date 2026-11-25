import itertools

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


def worst_slices(frame, y, p, cols, min_rows=120, top=6):
    y = np.asarray(y)
    p = np.asarray(p)
    overall = log_loss(y, p)
    found = []
    for k in (1, 2):
        for combo in itertools.combinations(cols, k):
            for key, idx in frame.groupby(list(combo), observed=True).indices.items():
                if len(idx) < min_rows or len(np.unique(y[idx])) < 2:
                    continue
                name = " & ".join(f"{c}={v}" for c, v in zip(combo, np.atleast_1d(key)))
                found.append((name, len(idx), log_loss(y[idx], p[idx], labels=[0, 1]) - overall))
    out = pd.DataFrame(found, columns=["slice", "rows", "gap"])
    return out.sort_values("gap", ascending=False).head(top).reset_index(drop=True)
