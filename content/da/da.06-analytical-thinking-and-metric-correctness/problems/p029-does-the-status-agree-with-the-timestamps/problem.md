# Does the status agree with the timestamps?

Chapter section 9.2. The `status` column and the timestamps describe the same facts, so they can contradict each other.
A metric that counts through the status and one that counts through the timestamp then disagree, and nobody knows why.
The chapter checks six contradictions. This time you list **which jobs** break which rule.

Write `lifecycle_problems(jobs)`.

`jobs` has `job_id`, `status`, `created_at`, `started_at`, `completed_at`, `cancelled_at`. Missing times are `NaT`.
The six rules, with the **exact label** each one uses:

| Label | A job breaks it when |
|---|---|
| `completed without completed_at` | status is `completed` and `completed_at` is missing |
| `completed_at on a non-completed job` | status is not `completed` and `completed_at` is present |
| `cancelled without cancelled_at` | status is `cancelled` and `cancelled_at` is missing |
| `cancelled but started` | status is `cancelled` and `started_at` is present |
| `completed before it started` | `completed_at < started_at` (both present) |
| `started before it was created` | `started_at < created_at` (both present) |

Return a **list of `(job_id, label)` tuples**, one for every rule a job breaks (a job can break several), sorted by
`job_id` and, for one job, in the order of the table above. A clean table gives `[]`. Do not change `jobs`.

## Example

```python
import pandas as pd

jobs = pd.DataFrame({
    "job_id": [1, 2],
    "status": ["completed", "pending"],
    "created_at": pd.to_datetime(["2025-02-01 09:00", "2025-02-02 09:00"]),
    "started_at": pd.to_datetime(["2025-02-02 10:00", None]),
    "completed_at": pd.to_datetime([None, "2025-02-03 10:00"]),
    "cancelled_at": pd.to_datetime([None, None]),
})
print(lifecycle_problems(jobs))
```

```text
[(1, 'completed without completed_at'), (2, 'completed_at on a non-completed job')]
```
