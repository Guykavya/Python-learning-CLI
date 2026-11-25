## Approach

Filter to the data that exist (`created_at < cut`), count per month label, then ask for each month whether it
has *ended*: its half-open end (the first instant of the next month) must be `<= cut`. If it is after the cut, the
month is partial. A month with a boundary cut (`cut` exactly on the 1st) is complete because the end is excluded.

## Code

```python
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
```

## Complexity

O(n) to filter and group, plus a few operations per month.

## Another way

`seen["created_at"].dt.to_period("M")` gives a month object, and `period.end_time` / `(period + 1).start_time` gives the
boundary. For a fair comparison, you can also compare only the first `k` days of every month, so that a partial month is
compared with the same part of the others (chapter 8.5).
