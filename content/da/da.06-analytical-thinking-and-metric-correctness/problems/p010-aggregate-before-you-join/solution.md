## Approach

Bring the finer table (payments) to the job grain first, so the join is one-to-one and cannot multiply `quote_total`.
Then group jobs by customer. Payments of unknown jobs fall away because a left join from `jobs` never sees them.

## Code

```python
def paid_per_customer(jobs, payments):
    paid_by_job = payments.groupby("job_id")["amount"].sum().rename("paid")
    per_job = jobs.merge(paid_by_job, on="job_id", how="left", validate="1:1")
    per_job["paid"] = per_job["paid"].fillna(0)
    out = per_job.groupby("customer_id").agg(quoted=("quote_total", "sum"), paid=("paid", "sum"))
    return out.astype(int)
```

## Complexity

Two passes of O(n + m).

## Another way

Skip the join: `jobs["job_id"].map(paid_by_job).fillna(0)` adds the column without a merge. Or group payments by the
customer after mapping each payment to its job's customer; but then `quoted` needs its own grouping on `jobs`.
