# A metric as code

Chapter section 7.3. A definition on a wiki page can drift from the code. Keep both in one object: a small frozen
dataclass that holds the promise, and one function that computes **any** metric from it.

Write, in `solution.py`:

1. A frozen dataclass `Metric` with these fields, in this order:
   `name` (text), `numerator` (a tuple of statuses counted in the numerator), `denominator` (`None` for a plain count, or a
   tuple of statuses for a rate), `date_basis` (the name of the timestamp column that places a job in a period),
   `exclusions` (a tuple of `customer_id`s that are never counted, default `()`).
2. `compute(metric, jobs, start, end)`:
   - keep the jobs whose `date_basis` column satisfies `start <= t < end` (half-open; a missing timestamp is outside);
   - drop the jobs of the excluded customers;
   - the numerator is how many of those jobs have a status in `metric.numerator`;
   - with `denominator is None` return that count as an `int`; otherwise divide by the number of those jobs whose status is in
     `metric.denominator`, and return `None` when it is 0.
   - `start` and `end` may be `pd.Timestamp` or date strings. Never change `jobs`.
3. A dict `METRICS` with exactly two registered metrics, each keyed by its own `name`:
   - `"jobs_completed"`: numerator `("completed",)`, no denominator, date basis `completed_at`, exclusion `(99,)` (the test account);
   - `"completion_rate"`: numerator `("completed",)`, denominator `("completed", "cancelled", "failed")`, date basis
     `created_at`, exclusion `(99,)`.

`jobs` has `job_id, customer_id, status, created_at, completed_at`.

## Example

```python
import pandas as pd
from solution import METRICS, compute

jobs = pd.DataFrame({
    "job_id": [1, 2, 3], "customer_id": [1, 99, 2], "status": ["completed", "completed", "cancelled"],
    "created_at": pd.to_datetime(["2025-02-01", "2025-02-05", "2025-02-10"]),
    "completed_at": pd.to_datetime(["2025-02-02", "2025-02-06", None]),
})
print(compute(METRICS["jobs_completed"], jobs, "2025-02-01", "2025-03-01"))
print(compute(METRICS["completion_rate"], jobs, "2025-02-01", "2025-03-01"))
```

prints

```text
1
0.5
```

Job 2 belongs to the test account 99 and is ignored. `jobs_completed`: only job 1 has a `completed_at` in February
(job 3 has none). `completion_rate`: jobs 1 and 3 were created in February; both are decided; 1 of 2 completed.
