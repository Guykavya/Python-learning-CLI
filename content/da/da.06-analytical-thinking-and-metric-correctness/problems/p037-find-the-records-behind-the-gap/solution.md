## Approach

Move both tables to the **same grain** (one number per job), subtract, and keep the jobs where the difference is not
zero. `Series.sub(other, fill_value=0)` treats a job missing on one side as 0, so jobs that appear on one side only
come out with their full amount (positive for the dashboard, negative for the ledger). Row counts per job decide the
label: different counts means the join repeated (or lost) rows; the same count with different sums means a wrong amount.
The check `unexplained == 0` is the bridge rule: the pieces must add up to the gap.

## Code

```python
import pandas as pd


def explain_gap(dashboard, sql_result):
    d_sum = dashboard.groupby("job_id")["amount"].sum()
    s_sum = sql_result.groupby("job_id")["amount"].sum()
    d_rows = dashboard.groupby("job_id").size()
    s_rows = sql_result.groupby("job_id").size()
    diff = d_sum.sub(s_sum, fill_value=0)
    gap = int(dashboard["amount"].sum() - sql_result["amount"].sum())
    by_job, reasons = {}, {}
    for job_id in sorted(diff.index):
        c = int(diff[job_id])
        if c == 0:
            continue
        job_id = int(job_id)
        by_job[job_id] = c
        if job_id not in s_sum.index:
            reasons[job_id] = "only in dashboard"
        elif job_id not in d_sum.index:
            reasons[job_id] = "only in sql result"
        elif d_rows[job_id] != s_rows[job_id]:
            reasons[job_id] = f"repeated rows: {int(d_rows[job_id])} rows in dashboard, {int(s_rows[job_id])} rows in sql result"
        else:
            reasons[job_id] = "amount differs"
    return {"gap": gap, "by_job": by_job, "reasons": reasons, "unexplained": gap - sum(by_job.values())}
```

## Complexity

O(n + m) for the four group-bys, plus O(k log k) for the k jobs. No row-by-row loop over the data, only over the jobs
that differ.

## Another way

`pd.concat([d_sum.rename("dash"), s_sum.rename("ledger")], axis=1).fillna(0)` puts the two sums side by side in a
table; `table["diff"] = table["dash"] - table["ledger"]` is the same step as `sub(..., fill_value=0)`, and the table
is a good thing to print in a report. For a fan-out you can then also test the chapter's rule: `diff == (lines - 1) * ledger`.
