# Total versus completed plus pending

Chapter section 12 (and 14.4). A dashboard shows, for February, **total volume** (jobs by `created_at`), **completed
volume** (jobs by `started_at` with status `completed`) and **pending volume** (jobs by `started_at` with status
`pending`). The parts do not add up to the total. Your job: say exactly which jobs are in each number, give every job
that is in only one of the two main sets a **reason**, and show that the bridge closes.

Write `volume_bridge(jobs, start, end)`.

`jobs` has `job_id`, `status`, `created_at`, `started_at` (a missing time is `NaT`). The period is `[start, end)`
(half-open; `start` and `end` are Timestamps or texts). Compute three **sets of job ids**:

- `T`: jobs **created** in the period (any status)
- `C`: jobs with status `completed` that **started** in the period
- `P`: jobs with status `pending` that **started** in the period (the dashboard's pending number)

Return a dict with:

- `"T"`, `"C"`, `"P"`: the three sets (of plain `int`s)
- `"reasons"`: a dict `{job_id: label}` for every job that is in **exactly one of `T` and `C`**:
  - in `T` only: by status, `"cancelled (never started)"` for `cancelled`, `"failed"` for `failed`,
    `"pending (no start date yet)"` for `pending`; any other status (so a `completed` job that started after the period)
    gets `"started after the month"`
  - in `C` only: `"created before the month, started in it"`
- `"steps"`: the bridge from `len(T)` to `len(C)`: a list of `(label, change)` for the reasons that occur, **sorted by
  label**: each `T`-only label as `("created in month, <label>", -count)`, then **last** the line
  `("created before the month, started in it", +count)`. Reasons that do not occur are left out.
- `"closes"`: `True` when `len(T) + sum of the changes == len(C)`

Do not change `jobs`.

## Example

```python
import pandas as pd

jobs = pd.DataFrame({
    "job_id": [1, 2, 3],
    "status": ["completed", "completed", "cancelled"],
    "created_at": pd.to_datetime(["2025-02-03 09:00", "2025-01-30 09:00", "2025-02-05 09:00"]),
    "started_at": pd.to_datetime(["2025-02-04 09:00", "2025-02-02 09:00", None]),
})
r = volume_bridge(jobs, "2025-02-01", "2025-03-01")
print(sorted(r["T"]), sorted(r["C"]), sorted(r["P"]))
print(r["steps"], r["closes"])
```

```text
[1, 3] [1, 2] []
[('created in month, cancelled (never started)', -1), ('created before the month, started in it', 1)] True
```
