## Approach

The dataclass is the promise; `compute` is the single place that turns any promise into a number. Because the same code
computes every metric, two metrics cannot disagree about how a month is cut. A missing timestamp compares False with both
bounds, so it is automatically outside the period.

## Code

```python
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Metric:
    name: str
    numerator: tuple
    denominator: object
    date_basis: str
    exclusions: tuple = ()


def compute(metric, jobs, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    basis = jobs[metric.date_basis]
    rows = jobs[(basis >= start) & (basis < end) & ~jobs["customer_id"].isin(metric.exclusions)]
    num = int(rows["status"].isin(metric.numerator).sum())
    if metric.denominator is None:
        return num
    den = int(rows["status"].isin(metric.denominator).sum())
    return num / den if den else None


METRICS = {
    "jobs_completed": Metric("jobs_completed", ("completed",), None, "completed_at", (99,)),
    "completion_rate": Metric("completion_rate", ("completed",), ("completed", "cancelled", "failed"), "created_at", (99,)),
}
```

## Complexity

O(n) per metric and period.

## Another way

The chapter keeps `compute` as a function stored in the object (a lambda). Storing the *data* of the definition (statuses,
column, exclusions) instead lets you print, compare and lint the definition (problem 23), which a lambda does not allow.
`dataclasses.replace(metric, exclusions=())` makes a variant without changing the original.
