## Approach

Convert first, then truncate: the date of a moment depends on the time zone, so the shift by 5 h 30 min has to come
before the date is taken. UTC clock times from 18:30:00 on are already the next day in India. A Series of shifted
times is a **new** Series, so `jobs` stays unchanged.

## Code

```python
import pandas as pd

IST = pd.Timedelta(hours=5, minutes=30)


def jobs_per_ist_day(jobs):
    local = jobs["created_at"] + IST
    counts = local.dt.strftime("%Y-%m-%d").value_counts().sort_index()
    return {day: int(n) for day, n in counts.items()}
```

## Complexity

O(n) to shift and format, O(d log d) to sort the d distinct days.

## Another way

`jobs["created_at"].dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata").dt.date` lets pandas know the zone and also
handles daylight saving time for other countries. It needs the time-zone database (`tzdata`); the fixed shift needs nothing.
