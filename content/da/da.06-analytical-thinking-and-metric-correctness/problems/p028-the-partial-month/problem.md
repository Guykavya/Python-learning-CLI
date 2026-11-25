# The partial month

Chapter section 8.5. The data were extracted on 5 April, so April holds only 5 days. A table that shows
"April: 8 jobs" next to "March: 973 jobs" invites a false conclusion. The label costs nothing.

Write `monthly_counts(jobs, cut)`.

- `jobs` has `job_id` and `created_at`. `cut` is the extraction moment (Timestamp or text).
- Keep only jobs created **before** `cut`. Count them per calendar month of `created_at`.
- Return a DataFrame with exactly the columns `month` (text such as `"2025-03"`), `jobs` (int) and `is_partial` (bool),
  one row per month that has at least one job, sorted by month, with a fresh index `0, 1, 2, ...`.
- `is_partial` is `True` when the month **has not ended** at the cut: the first instant of the next month is **after**
  `cut`. If the cut is exactly at the first instant of a month, the previous month is complete.
- Do not change `jobs`.

## Example

```python
import pandas as pd

jobs = pd.DataFrame({"job_id": [1, 2, 3, 4],
                     "created_at": pd.to_datetime(["2025-02-10 09:00", "2025-03-31 23:00", "2025-04-02 09:00", "2025-04-04 09:00"])})
print(monthly_counts(jobs, "2025-04-05").to_dict("records"))
```

```text
[{'month': '2025-02', 'jobs': 1, 'is_partial': False}, {'month': '2025-03', 'jobs': 1, 'is_partial': False}, {'month': '2025-04', 'jobs': 2, 'is_partial': True}]
```
