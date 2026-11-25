## Approach

Two filters on `created_at` and two shares. "Age at least `min_age_days`" is the same as "created no later than
`cut - min_age_days`", so one comparison with `<=` handles the boundary. The mean of a boolean Series is the share of
`True`, which avoids a manual division; an empty group must be handled before (the mean of nothing is `NaN`).

## Code

```python
import pandas as pd


def mature_completion_rate(jobs, cut, min_age_days):
    cut = pd.Timestamp(cut)
    seen = jobs[jobs["created_at"] < cut]
    mature = seen[seen["created_at"] <= cut - pd.Timedelta(days=min_age_days)]
    naive = float(seen["status"].eq("completed").mean()) if len(seen) else None
    rate = float(mature["status"].eq("completed").mean()) if len(mature) else None
    return {"naive": naive, "mature": rate, "jobs": len(seen), "mature_jobs": len(mature)}
```

## Complexity

O(n): two boolean filters over the table.

## Another way

Add a column `age_days = (cut - created_at).dt.total_seconds() / 86400` and filter on `age_days >= min_age_days`. It is
easier to read but floating-point days can misplace a job that is exactly on the boundary; comparing timestamps is exact.
Also useful: report `pending` count next to the rate, or exclude pending from the denominator (chapter 7.2, definition 2).
