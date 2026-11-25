# Which denominator?

Chapter sections 5.3 and 7.2. "Completion rate" has at least three honest denominators. Compute all three for the jobs
**created** in a period and see how far apart they are.

`jobs` has `job_id`, `created_at`, `status` (`completed`, `cancelled`, `failed`, `pending`) and `started_at` (missing when
the job has not started). Write `completion_rates(jobs, start, end)`. The cohort is the jobs with
`start <= created_at < end` (half-open). Return a dict with exactly these keys, all with the same numerator
(cohort jobs whose status is `completed`):

- `"completed_per_created"`: divided by all jobs of the cohort;
- `"completed_per_started"`: divided by cohort jobs that have a `started_at`;
- `"completed_per_decided"`: divided by cohort jobs whose status is `completed`, `cancelled` or `failed`.

A rate whose denominator is 0 is `None`. `start` and `end` may be `pd.Timestamp` or date strings. Never change `jobs`.

## Example

```python
import pandas as pd
from solution import completion_rates

jobs = pd.DataFrame({
    "created_at": pd.to_datetime(["2025-02-01", "2025-02-02", "2025-02-03", "2025-03-01"]),
    "status": ["completed", "cancelled", "pending", "completed"],
    "started_at": pd.to_datetime(["2025-02-02", None, None, "2025-03-02"]),
})
r = completion_rates(jobs, "2025-02-01", "2025-03-01")
for k, v in r.items():
    print(k, v)
```

prints

```text
completed_per_created 0.3333333333333333
completed_per_started 1.0
completed_per_decided 0.5
```

Three February jobs (the fourth is created exactly at the end, so it is March's): 1 completed. Over all 3 created: one third.
Over the 1 started: 100 percent, because the cancellation never started. Over the 2 decided: one half.
