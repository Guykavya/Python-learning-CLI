## Approach

Fix the cohort once, then divide one numerator by three denominators. The subset rule holds for all three: completed jobs
are created, completed jobs have started, and completed jobs are decided. A helper turns a zero denominator into `None`.

## Code

```python
import pandas as pd


def _ratio(num, den):
    return num / den if den else None


def completion_rates(jobs, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    cohort = jobs[(jobs["created_at"] >= start) & (jobs["created_at"] < end)]
    status = cohort["status"]
    completed = int((status == "completed").sum())
    created = len(cohort)
    started = int(cohort["started_at"].notna().sum())
    decided = int(status.isin(["completed", "cancelled", "failed"]).sum())
    return {
        "completed_per_created": _ratio(completed, created),
        "completed_per_started": _ratio(completed, started),
        "completed_per_decided": _ratio(completed, decided),
    }
```

## Complexity

O(n) for the filter and the counts.

## Another way

Return the counts too (`completed`, `created`, ...) and compute the rates from them, so a report can show "3 of 8".
The chapter's rule 3 of metric hygiene: a rate shows its numerator and denominator.
