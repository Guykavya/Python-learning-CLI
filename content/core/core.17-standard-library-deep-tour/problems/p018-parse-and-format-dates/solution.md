## Approach

Every parser is "copy the sample text, replace each part by its code":

| text | format |
|---|---|
| `2025-03-14 09:05:30` | `%Y-%m-%d %H:%M:%S` |
| `03/14/2025` | `%m/%d/%Y` |

`strptime` checks the text strictly: a missing part, an extra part, February 30th or hour 25 all
raise `ValueError`. It always returns a `datetime`; `.date()` drops the time part.

`isoformat()` writes the ISO 8601 form with a `T` separator, and `datetime.fromisoformat`
reads it back exactly. Use ISO for anything a machine will read again.

For `pretty`, the day without a leading zero is the catch. The C library's `strftime` has
`%-d` on Linux and macOS and `%#d` on Windows, but nothing that works everywhere. Python's `int`
already prints without a zero, so `dt.day` does the job. An f-string accepts `strftime` codes
after the colon: `f"{dt:%b %Y}"`.

## Code

```python
from datetime import date, datetime


def parse_log_stamp(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")


def parse_us_date(text: str) -> date:
    return datetime.strptime(text, "%m/%d/%Y").date()


def to_iso(dt: datetime) -> str:
    return dt.isoformat()


def pretty(dt: datetime) -> str:
    return f"{dt:%a} {dt.day} {dt:%b %Y, %H:%M}"
```

## Complexity

O(1) for each call (the strings have fixed, small length).

## Another way

`datetime.fromisoformat("2025-03-14 09:05:30")` also accepts a space instead of the `T`, so
`parse_log_stamp` could use it. It is more lenient (it also accepts a date alone), which is
good for reading ISO data but worse for validating that a log line has exactly the expected
shape. `%a` and `%b` follow the current locale; Python programs use the "C" locale unless they
call `locale.setlocale`, so you get English names by default.
