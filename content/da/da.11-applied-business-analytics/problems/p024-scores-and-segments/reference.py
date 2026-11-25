import pandas as pd


def score_quantile(s, higher_is_better=True, n=5):
    r = s.rank(method="first", ascending=higher_is_better)
    return pd.qcut(r, n, labels=list(range(1, n + 1))).astype(int)


def segment(r, f):
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / promising"
    if r <= 2 and f >= 3:
        return "At risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    return "Needs attention"
