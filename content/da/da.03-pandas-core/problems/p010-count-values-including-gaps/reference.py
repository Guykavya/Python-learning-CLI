import pandas as pd


def category_counts(s):
    """Frequency table with missing values shown as '(missing)'."""
    labels = s.astype("object").where(s.notna(), "(missing)")
    counts = labels.value_counts()
    out = pd.DataFrame({"label": counts.index.astype(str), "count": counts.to_numpy()})
    out["share"] = out["count"] / len(s)
    out = out.sort_values(["count", "label"], ascending=[False, True])
    return out.reset_index(drop=True)
