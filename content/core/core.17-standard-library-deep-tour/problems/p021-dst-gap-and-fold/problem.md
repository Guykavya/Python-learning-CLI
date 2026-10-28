# Trace: the DST gap and the DST fold

Twice a year, many places move their clocks. In spring an hour is **skipped** (the *gap*): in
New York the wall clock jumps from 01:59 straight to 03:00, so a time such as 02:30 never happens
that day. In autumn an hour is **repeated** (the *fold*): the wall clock reaches 01:59, goes back
to 01:00, and runs through the same hour again, so 01:30 happens twice.

The dates used here (real rules, they do not change):

| Zone | Spring forward (gap) | Fall back (fold) |
|---|---|---|
| `America/New_York` | Sun 10 March 2024: 02:00 EST becomes 03:00 EDT | Sun 3 November 2024: 02:00 EDT becomes 01:00 EST |
| `Europe/London` | Sun 31 March 2024: 01:00 GMT becomes 02:00 BST | Sun 27 October 2024: 02:00 BST becomes 01:00 GMT |

EST is UTC-5, EDT is UTC-4, GMT is UTC+0, BST is UTC+1.

Predict **every line** this program prints:

```python
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ny = ZoneInfo("America/New_York")
london = ZoneInfo("Europe/London")
UTC = timezone.utc


def show(tag, dt):
    print(tag, dt.isoformat(), dt.tzname())


# 1. An ordinary winter day and summer day
show("A", datetime(2024, 1, 15, 12, 0, tzinfo=ny))
show("B", datetime(2024, 7, 15, 12, 0, tzinfo=ny))

# 2. Spring forward: Sunday 10 March 2024, clocks jump 02:00 -> 03:00
gap = datetime(2024, 3, 10, 2, 30, tzinfo=ny)
show("C", gap)
show("D", gap.astimezone(UTC).astimezone(ny))

before = datetime(2024, 3, 9, 9, 0, tzinfo=ny)
later = before + timedelta(days=1)
show("E", later)
print("F", later - before)
print("G", later.astimezone(UTC) - before.astimezone(UTC))

# 3. Fall back: Sunday 3 November 2024, clocks go 02:00 -> 01:00
first = datetime(2024, 11, 3, 1, 30, tzinfo=ny)
second = first.replace(fold=1)
show("H", first)
show("I", second)
print("J", first == second)
print("K", second.astimezone(UTC) - first.astimezone(UTC))

u = datetime(2024, 11, 3, 5, 30, tzinfo=UTC)
show("L", u.astimezone(ny))
show("M", (u + timedelta(hours=1)).astimezone(ny))
print("N", (u + timedelta(hours=1)).astimezone(ny).fold)

# 4. London's gap: Sunday 31 March 2024, clocks jump 01:00 -> 02:00
show("O", datetime(2024, 3, 31, 1, 30, tzinfo=london))
show("P", datetime(2024, 3, 31, 1, 30, tzinfo=london).astimezone(UTC).astimezone(london))
```

Rules you need (all from the chapter):

- `dt.isoformat()` prints the date, the time and the UTC offset, for example `2024-01-15T12:00:00-05:00`.
- A `datetime` has a `fold` attribute, `0` or `1`. It only matters for a wall time that happens
  twice: `fold=0` means the first time, `fold=1` the second. For a time in the **gap** (that never
  happens), `fold=0` uses the offset that was in force **before** the jump.
- `aware + timedelta(...)` does **wall-clock** arithmetic: it moves the date and the clock face,
  keeps the zone, then works out the offset for the new wall time.
- Subtracting or comparing two aware datetimes with the **same** `tzinfo` object ignores the
  offsets and `fold` (it compares wall clocks). With different `tzinfo`s, both are turned into UTC first.
- `print` of a `timedelta` looks like `1 day, 0:00:00`, `23:00:00` or `1:00:00`.

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it.

**Example** (the first line, given away):

```text
A 2024-01-15T12:00:00-05:00 EST
```

(You can check your answer on your own machine only if it has time-zone data. On Windows that
means `.venv/Scripts/python -m pip install tzdata` first. Try to work it out by hand before you run anything.)
