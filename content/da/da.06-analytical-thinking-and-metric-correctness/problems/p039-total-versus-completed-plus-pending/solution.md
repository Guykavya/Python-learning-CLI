## Approach

The three dashboard numbers are three **different sets of jobs** because they use different date bases (created against
started) and different statuses. So compare the sets, not the numbers.

1. Masks for the half-open period: `created` and `started` (a `NaT` start is never in a period).
2. `T = created`, `C = started & completed`, `P = started & pending`. `P` can never contain a job that has not started,
   so a "pending volume" by start date misses every waiting job (job 6).
3. For a job in `T` but not in `C`: its status gives the reason (cancelled, failed, pending); a completed job that is in
   `T` but not in `C` must have started after the period. For a job in `C` but not in `T`: it was created earlier.
4. Count the reasons and build the bridge `len(T) -> len(C)`. It closes by construction, because the jobs of `T` are
   either in `C` or have exactly one reason, and the jobs of `C` are either in `T` or have the "created earlier" reason.

## Code

```python
import pandas as pd


def volume_bridge(jobs, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    created = (jobs["created_at"] >= start) & (jobs["created_at"] < end)
    started = (jobs["started_at"] >= start) & (jobs["started_at"] < end)
    in_t = created
    in_c = started & jobs["status"].eq("completed")
    in_p = started & jobs["status"].eq("pending")
    ids = lambda m: {int(j) for j in jobs.loc[m, "job_id"]}
    t_only = jobs[in_t & ~in_c]
    c_only = jobs[in_c & ~in_t]
    names = {"cancelled": "cancelled (never started)", "failed": "failed", "pending": "pending (no start date yet)"}
    reasons = {int(r.job_id): names.get(r.status, "started after the month") for r in t_only.itertuples()}
    reasons.update({int(j): "created before the month, started in it" for j in c_only["job_id"]})
    counts = {}
    for job_id, label in reasons.items():
        counts[label] = counts.get(label, 0) + 1
    late = "created before the month, started in it"
    steps = [(f"created in month, {label}", -n) for label, n in sorted(counts.items()) if label != late]
    if late in counts:
        steps.append((late, counts[late]))
    closes = int(in_t.sum()) + sum(change for _, change in steps) == int(in_c.sum())
    return {"T": ids(in_t), "C": ids(in_c), "P": ids(in_p), "reasons": reasons, "steps": steps, "closes": closes}
```

## Complexity

O(n) for the masks; the loops run only over the jobs that are in exactly one set. The sort is over a handful of labels.

## Another way

Give every job one bucket in a single pass with `np.select` (`in both`, `cancelled`, `failed`, ...), then
`value_counts()`; the chapter's SQL version does the same with a `CASE WHEN`. Passing the steps to the `bridge` function
of the previous problem turns them into a printed report.
