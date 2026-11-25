import numpy as np


def confusion_at(y, p, threshold):
    y = np.asarray(y).astype(bool)
    pred = np.asarray(p, dtype=float) >= threshold
    return {
        "TP": int(np.sum(y & pred)),
        "FP": int(np.sum(~y & pred)),
        "FN": int(np.sum(y & ~pred)),
        "TN": int(np.sum(~y & ~pred)),
    }
