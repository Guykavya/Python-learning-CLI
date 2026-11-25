## Approach

One helper holds the half-open February test, so every definition cuts the month in exactly the same way. The definitions
differ only in the timestamp column, the status filter and the clock. A missing timestamp compares False and is never counted.

## Code

```python
import pandas as pd

FEB_START = pd.Timestamp("2025-02-01")
FEB_END = pd.Timestamp("2025-03-01")
IST = pd.Timedelta(hours=5, minutes=30)


def _in_feb(s):
    return (s >= FEB_START) & (s < FEB_END)


def completed_in_february(jobs, definition):
    done = jobs["status"].eq("completed")
    if definition == "by_created":
        mask = _in_feb(jobs["created_at"])
    elif definition == "by_started":
        mask = _in_feb(jobs["started_at"])
    elif definition == "by_completed":
        mask = done & _in_feb(jobs["completed_at"])
    elif definition == "by_completed_ist":
        mask = done & _in_feb(jobs["completed_at"] + IST)
    else:
        raise ValueError(f"unknown definition: {definition!r}")
    return int(mask.sum())
```

## Complexity

O(n) per call.

## Another way

A dict `{name: function}` replaces the `if` chain and makes it easy to list the definitions. For a real IST conversion,
`tz_localize("UTC").dt.tz_convert("Asia/Kolkata")` gives the same result, because India has no daylight saving time.
