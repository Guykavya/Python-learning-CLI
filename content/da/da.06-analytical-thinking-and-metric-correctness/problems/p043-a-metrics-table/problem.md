# A metrics table

Chapter sections 14.2 and 14.3. Every metric is defined **once**, as data: a `MetricSpec` holds the name, the unit and a
function `fn(ctx, start, end)` that returns **`(value, numerator, denominator)`**. A table of metrics then needs no
metric-specific code: it just calls every function for every month. A rate is never shown without the counts behind it.

You are given objects with (at least) these attributes; the test builds them, you only read them:

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class MetricSpec:
    name: str          # "jobs_created"
    unit: str          # "jobs", "rupees", "share of jobs", ...
    fn: Callable       # fn(ctx, start, end) -> (value, numerator, denominator); start and end are pd.Timestamp
```

Write `metrics_table(ctx, specs, months)`.

- `ctx` is a dict of tables, passed unchanged to every `fn`.
- `specs` is a list of such objects. `months` is a dict `{label: (start_text, end_text)}`, for example
  `{"Jan": ("2025-01-01", "2025-02-01"), "Feb": ("2025-02-01", "2025-03-01")}`; each period is half-open.
- Call `spec.fn(ctx, pd.Timestamp(start_text), pd.Timestamp(end_text))` for **every spec and every month**.
- Return a DataFrame with the columns `metric`, `month`, `unit`, `numerator`, `denominator`, `value`: **one row per
  metric and month**, metrics in the order of `specs`, and for each metric the months in the order of `months`.
  `metric` is the spec's `name`, `month` is the label, `unit` is the spec's `unit`.
- `numerator`, `denominator` and `value` are exactly what `fn` returned. When `fn` returns `None` as the denominator
  (a count, not a rate), the cell is missing (`NaN`).
- The index is `0, 1, 2, ...`. Do not change `ctx`.

## Example

```python
import pandas as pd

ctx = {"jobs": pd.DataFrame({"job_id": [1, 2, 3],
                             "created_at": pd.to_datetime(["2025-01-10 09:00", "2025-02-01 00:00", "2025-02-15 09:00"])})}


def created(ctx, start, end):
    j = ctx["jobs"]
    n = int(((j["created_at"] >= start) & (j["created_at"] < end)).sum())
    return n, n, None


specs = [MetricSpec("jobs_created", "jobs", created)]
months = {"Jan": ("2025-01-01", "2025-02-01"), "Feb": ("2025-02-01", "2025-03-01")}
t = metrics_table(ctx, specs, months)
print(t[["metric", "month", "numerator", "value"]].to_dict("records"))
```

```text
[{'metric': 'jobs_created', 'month': 'Jan', 'numerator': 1, 'value': 1}, {'metric': 'jobs_created', 'month': 'Feb', 'numerator': 2, 'value': 2}]
```
