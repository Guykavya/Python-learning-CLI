import pandas as pd


def monthly_counts(jobs, cut):
    cut = pd.Timestamp(cut)
    seen = jobs[jobs["created_at"] < cut]
    counts = seen.groupby(seen["created_at"].dt.strftime("%Y-%m")).size()
    out = counts.rename("jobs").rename_axis("month").reset_index()
    next_start = pd.to_datetime(out["month"] + "-01") + pd.offsets.MonthBegin(1)
    out["is_partial"] = (next_start > cut).to_numpy()
    out["jobs"] = out["jobs"].astype(int)
    return out
