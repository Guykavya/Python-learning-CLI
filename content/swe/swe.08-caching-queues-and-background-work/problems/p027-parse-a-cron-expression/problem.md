# Parse a cron expression

Chapter section 14.1 (cron expressions). Write a parser for the five-field cron notation and a function that finds the next run time. Schedulers (cron, Celery beat, arq, Kubernetes) all read this notation; knowing its rules lets you read a schedule correctly.

```text
 minute (0-59)  hour (0-23)  day of month (1-31)  month (1-12)  day of week (0-6, 0 = Sunday)
```

Each field is a comma-separated list of parts. A part is `*` (every value), a number, a range `a-b`, or any of these followed by a step `/n`: `*/15`, `0-30/10`, `5/10` (from 5 to the end of the field, every 10).

## What to write

```python
FIELDS = [("minute", 0, 59), ("hour", 0, 23), ("day", 1, 31), ("month", 1, 12), ("weekday", 0, 6)]

def parse_field(text: str, low: int, high: int, name: str = "field") -> set[int]: ...

class Cron:
    def __init__(self, expression: str): ...
    def next_after(self, after: datetime) -> datetime: ...
    def between(self, start: datetime, end: datetime): ...      # a generator: start < t <= end
```

- `parse_field` returns the set of allowed values. Raise `ValueError` **whose message contains `name`** for anything invalid: a value outside `low..high`, a range whose start is after its end, a step below 1, an empty part, a non-number.
- `Cron(expression)`: exactly 5 fields separated by spaces, or `ValueError`. Parse each field with its name, so a bad hour says `hour`.
- **Day rule:** if both day-of-month and day-of-week are restricted (neither is `*`), a day matches when **either** matches. Otherwise both must match (one of them is `*`, so that means "the other one"). Python's `weekday()` is Monday = 0; cron is Sunday = 0: use `(d.weekday() + 1) % 7`.
- `next_after(after)` is the first matching minute **strictly after** `after` (seconds are always 0). Search day by day for at most 5 years, then raise `ValueError`.
- `between(start, end)` yields every run time `t` with `start < t <= end`, in order.

## Example

```python
now = datetime(2026, 11, 6, 9, 0)                  # a Friday
Cron("*/15 * * * *").next_after(now)               # 2026-11-06 09:15
Cron("0 9 * * 1-5").next_after(now)                # 2026-11-09 09:00 (Monday)
Cron("0 0 29 2 *").next_after(now)                 # 2028-02-29 00:00
Cron("0 8 13 * 5").next_after(now)                 # 2026-11-13 08:00 (the 13th OR a Friday)
parse_field("0-30/10", 0, 59)                      # {0, 10, 20, 30}
Cron("0 25 * * *")                                 # ValueError: ... hour ...
```
