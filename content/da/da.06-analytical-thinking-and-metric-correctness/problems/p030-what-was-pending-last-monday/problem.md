# What was pending last Monday?

Chapter section 9.3. The `status` column is a **snapshot** of the present. To know which jobs were still open on an
earlier date, you cannot filter on today's `status`: a job that is `completed` today may have been waiting last Monday.
You must rebuild the past from the timestamps.

Write `pending_on(jobs, when)`.

- `jobs` has `job_id`, `status`, `created_at`, `completed_at`, `cancelled_at` (missing times are `NaT`). `when` is a Timestamp or text.
- A job was **open** at `when` if it had been created (`created_at <= when`) and had **not yet** been completed
  (`completed_at` missing or `> when`) and **not yet** been cancelled (`cancelled_at` missing or `> when`).
  An event at exactly `when` has already happened.
- A `failed` job has no failure time, so the table cannot say when it stopped being open. As in the chapter, it counts as
  open from its creation on (the answer is an **upper bound**).
- Return the **sorted list of `job_id`s** (plain `int`s). Do not use today's `status` for anything except what is said above:
  the rule uses only the timestamps. Do not change `jobs`.

## Example

```python
import pandas as pd

jobs = pd.DataFrame({
    "job_id": [1, 2, 3],
    "status": ["completed", "cancelled", "pending"],
    "created_at": pd.to_datetime(["2025-02-01 09:00", "2025-02-01 09:00", "2025-02-12 09:00"]),
    "completed_at": pd.to_datetime(["2025-02-15 09:00", None, None]),
    "cancelled_at": pd.to_datetime([None, "2025-02-03 09:00", None]),
})
print(pending_on(jobs, "2025-02-10 00:00"))
```

```text
[1]
```
