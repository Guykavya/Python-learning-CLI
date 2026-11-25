import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def slice_table(frame, y, p, col):
    y = np.asarray(y)
    p = np.asarray(p)
    rows = []
    for value, idx in frame.groupby(col, observed=True).indices.items():
        auc = roc_auc_score(y[idx], p[idx]) if len(np.unique(y[idx])) == 2 else np.nan
        rows.append((value, len(idx), float(y[idx].mean()), float(p[idx].mean()), auc))
    out = pd.DataFrame(rows, columns=[col, "rows", "base_rate", "mean_p", "auc"]).set_index(col)
    return out.sort_index()
