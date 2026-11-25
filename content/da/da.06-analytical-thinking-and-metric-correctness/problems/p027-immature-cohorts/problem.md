# Immature cohorts

Chapter section 8.4. The newest jobs have not had time to finish, so a completion rate that includes them looks too
low. A cohort is **mature** when every job in it is old enough to have been decided.

Write `mature_completion_rate(jobs, cut, min_age_days)`.

- `jobs` has `job_id`, `created_at` and `status` (`completed`, `cancelled`, `failed`, `pending`).
  `cut` is the moment the data were extracted (a Timestamp or text).
- Consider only jobs created **before** `cut`.
- **naive rate** = completed jobs / all those jobs.
- A job is **mature** when its age at the cut is **at least** `min_age_days` days: `created_at <= cut - min_age_days days`
  (a job exactly `min_age_days` old is mature).
- **mature rate** = completed jobs among the mature jobs / mature jobs. If there are no mature jobs, it is `None`.
- Return a dict: `{"naive": ..., "mature": ..., "jobs": n_all, "mature_jobs": n_mature}`. Rates are floats (not rounded).
- Do not change `jobs`.

## Example

```python
import pandas as pd

jobs = pd.DataFrame({
    "job_id": [1, 2, 3, 4],
    "created_at": pd.to_datetime(["2025-03-01", "2025-03-10", "2025-03-30", "2025-04-02"]),
    "status": ["completed", "cancelled", "pending", "pending"],
})
print(mature_completion_rate(jobs, "2025-04-05", 14))
```

```text
{'naive': 0.25, 'mature': 0.5, 'jobs': 4, 'mature_jobs': 2}
```
