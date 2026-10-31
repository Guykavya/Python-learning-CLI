## Approach

- **days_between**: subtracting dates gives a `timedelta`; `.days` is the whole-day count.
  `abs()` makes the order irrelevant. Month lengths and leap years are handled by the library.
- **add_business_days**: walk one calendar day at a time in the right direction, and count
  only the days whose `weekday()` is 0 to 4. Stop when the count is used up. Because the walk
  counts the days you **land on**, starting on a Saturday and moving 1 lands on Monday.
- **age_on**: the difference in years, minus one if this year's birthday is still ahead. Comparing
  `(month, day)` tuples does that in one line, and it handles 29 February by itself: `(2, 28)` is
  before `(2, 29)` and `(3, 1)` is after it.
- **format_duration**: a `timedelta` is normalised to `days`, `seconds` (0 to 86399) and
  `microseconds`. `divmod` splits the seconds into hours, minutes and seconds; `:02d` pads them.
  A negative timedelta has negative `days` and positive `seconds` (`timedelta(seconds=-1)` is
  `-1 day, 23:59:59`), which is why it is rejected instead of formatted.

## Code

```python
from datetime import date, timedelta


def days_between(a: date, b: date) -> int:
    return abs((b - a).days)


def add_business_days(start: date, n: int) -> date:
    step = timedelta(days=1 if n >= 0 else -1)
    day = start
    left = abs(n)
    while left > 0:
        day += step
        if day.weekday() < 5:
            left -= 1
    return day


def age_on(birth: date, today: date) -> int:
    years = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        years -= 1
    return years


def format_duration(td: timedelta) -> str:
    if td < timedelta(0):
        raise ValueError(f"negative duration: {td}")
    hours, rest = divmod(td.seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{td.days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
```

## Complexity

`add_business_days` is O(|n|) (about 1.4 steps per working day). Everything else is O(1).

## Another way

Business days in O(1): whole weeks are `n // 5` weeks of 7 days, then walk the remaining 0 to 4
days. It is faster for huge `n` but full of edge cases (starting on a weekend, going backwards).
For real calendars with public holidays you would keep a `set` of holiday dates and skip those
too, and for big date ranges a library such as NumPy's `busday_offset` does it for you.
