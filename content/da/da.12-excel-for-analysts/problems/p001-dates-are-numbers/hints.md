## Hint 1

Which date is serial number 0 for the dates of the 20th and 21st century? Subtract it from the date you are given and express the difference in days (a `timedelta` has `total_seconds()`).

## Hint 2

```text
EPOCH = datetime(1899, 12, 30)
to_serial: (d - EPOCH).total_seconds() / 86400     (turn a date into a datetime first)
from_serial: EPOCH + timedelta(days=n)
```
