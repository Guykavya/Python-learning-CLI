# One name, four definitions

Chapter sections 1.2, 7.2 and 8.3. "How many jobs in February?" has at least four honest answers. Write one function that
computes all four, so you can see them side by side.

`jobs` has `job_id, status, created_at, started_at, completed_at`. All timestamps are naive **UTC**. IST is UTC plus
5 hours 30 minutes. February is the half-open interval `[2025-02-01, 2025-03-01)`. Write
`completed_in_february(jobs, definition)` where `definition` is one of:

- `"by_created"`: jobs with `created_at` in February (any status);
- `"by_started"`: jobs with `started_at` in February (any status);
- `"by_completed"`: jobs with status `completed` **and** `completed_at` in February (UTC);
- `"by_completed_ist"`: the same, but February is cut on the **IST clock** (add 5:30 to `completed_at` before testing).

Return the number of jobs as a plain `int`. Any other `definition` raises `ValueError` whose message contains the name.
Never change `jobs` (compute the shifted clock without touching the column).

## Example

```python
import pandas as pd
from solution import completed_in_february

jobs = pd.DataFrame({
    "created_at": pd.to_datetime(["2025-01-30 09:00", "2025-02-02 09:00"]),
    "started_at": pd.to_datetime(["2025-02-01 08:00", "2025-02-03 08:00"]),
    "completed_at": pd.to_datetime(["2025-02-28 20:00", "2025-02-05 08:00"]),
    "status": ["completed", "completed"],
})
for d in ("by_created", "by_started", "by_completed", "by_completed_ist"):
    print(d, completed_in_february(jobs, d))
```

prints

```text
by_created 1
by_started 2
by_completed 2
by_completed_ist 1
```

Job 1 was created in January and started on 1 February; it completes on 28 February at 20:00 UTC, which is already
1 March on the IST clock (01:30), so `by_completed` counts it and `by_completed_ist` does not. Job 2 is February
in every definition. The same two jobs give 1 or 2 depending on the definition: that is why the definition belongs in the name.
