## Approach

Validate from the outside in: shape, then digits, then month, then day. Each step can assume the
previous ones passed, so each message can be precise. Only the `int()` conversions can raise by
themselves, so only they go in a `try`; the handler translates the low-level `ValueError` into a
message about dates, `from None` because the original adds nothing.

## Code

```python
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def parse_date(text):
    """Return (year, month, day) for 'YYYY-MM-DD'; raise ValueError with a helpful message."""
    parts = text.strip().split("-")
    if len(parts) != 3 or [len(p) for p in parts] != [4, 2, 2]:
        raise ValueError(f"date must look like YYYY-MM-DD, for example 2025-03-14, got {text!r}")
    try:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        raise ValueError(f"date must use digits only, like 2025-03-14, got {text!r}") from None
    if not 1 <= month <= 12:
        raise ValueError(f"month must be from 1 to 12, got {month}")
    last = DAYS[month - 1]
    if month == 2 and is_leap(year):
        last = 29
    if not 1 <= day <= last:
        raise ValueError(f"day must be from 1 to {last} for {year}-{month:02d}, got {day}")
    return year, month, day
```

## Complexity

O(n) in the length of the text.

## Another way

The standard library's `datetime.date.fromisoformat("2025-03-14")` does all of this (a later
module). Its messages are less friendly (`Invalid isoformat string`), so real programs often catch
its `ValueError` and raise their own message, exactly as here.
