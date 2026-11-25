import pandas as pd


def segment_table(o, dim, before, after):
    cols = {}
    for name, (start, end) in (("before", before), ("after", after)):
        rows = o[o["month"].between(pd.Period(start, "M"), pd.Period(end, "M"))]
        cols[f"{name} share %"] = rows[dim].value_counts(normalize=True) * 100
        cols[f"{name} churn %"] = rows.groupby(dim)["churned"].mean() * 100
    t = pd.DataFrame(cols).dropna()
    t["change (points)"] = t["after churn %"] - t["before churn %"]
    t = t[["before share %", "after share %", "before churn %", "after churn %", "change (points)"]]
    t.index.name = dim
    return t.sort_values("change (points)", ascending=False)
