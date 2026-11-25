## Approach

A serial number is a count of days, and a day has 86,400 seconds, so the fraction of a day is the time. The "epoch" 30 December 1899 makes the counts agree with Excel from March 1900 on.

## Code

```python
from datetime import date, datetime, timedelta

EPOCH = datetime(1899, 12, 30)


def to_serial(d):
    if not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)
    return (d - EPOCH).total_seconds() / 86400


def from_serial(n):
    return EPOCH + timedelta(days=float(n))
```

## Complexity

O(1).

## Another way

`openpyxl.utils.datetime.to_excel` and `from_excel` do the same; writing them once shows that a date format only changes how the number looks.
