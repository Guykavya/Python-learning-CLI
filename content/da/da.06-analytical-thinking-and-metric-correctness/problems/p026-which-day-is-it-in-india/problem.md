# Which day is it in India?

Chapter section 8.3. QuickFix stores every timestamp in **UTC**, but the business lives in India, where local time (IST)
is UTC plus 5 hours 30 minutes. A job created at 20:00 UTC on 31 January is, for the customer, 01:30 on 1 February.

Write `jobs_per_ist_day(jobs)`.

- `jobs` is a DataFrame with `job_id` and `created_at` (timestamps in UTC, no time-zone attached).
- Shift every `created_at` by `+5:30`, take the **calendar date**, and count the jobs per date.
- Return a plain `dict` `{"YYYY-MM-DD": count}` with the dates in increasing order. Dates with no job are not listed.
- Do not change `jobs`.

(You may add a `pd.Timedelta(hours=5, minutes=30)` or use `tz_localize("UTC").dt.tz_convert("Asia/Kolkata")`; for India
the two give the same answer, because India has no daylight saving time.)

## Example

```python
import pandas as pd

jobs = pd.DataFrame({
    "job_id": [1, 2, 3],
    "created_at": pd.to_datetime(["2025-01-31 10:00", "2025-01-31 20:00", "2025-02-01 02:00"]),
})
print(jobs_per_ist_day(jobs))
```

```text
{'2025-01-31': 1, '2025-02-01': 2}
```
