## Approach

One numerator, two denominators. The numerator uses `isin` so that lines of unknown jobs fall away. The denominators come
from `jobs`, not from `items`: a job with no lines is still a job, and a customer is counted once however many jobs they have.

## Code

```python
def _items_of_known_jobs(jobs, items):
    return int(items["job_id"].isin(jobs["job_id"]).sum())


def items_per_job(jobs, items):
    n_jobs = jobs["job_id"].nunique()
    return float(_items_of_known_jobs(jobs, items) / n_jobs) if n_jobs else None


def items_per_customer(jobs, items):
    n_customers = jobs["customer_id"].nunique()
    return float(_items_of_known_jobs(jobs, items) / n_customers) if n_customers else None
```

## Complexity

O(n + m).

## Another way

`items.groupby("job_id").size().reindex(jobs["job_id"], fill_value=0).mean()` gives the per-job average with an explicit
zero for jobs without lines. A third honest number, the average of each customer's own average, is yet another question.
