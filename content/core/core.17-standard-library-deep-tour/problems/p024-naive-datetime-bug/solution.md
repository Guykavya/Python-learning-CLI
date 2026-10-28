## Approach

There are four separate bugs, all from treating times as if they had no zone:

1. **`parse_local` returned a naive datetime.** It ignored `zone`. Fix: attach the zone with
   `replace(tzinfo=ZoneInfo(zone))`. `replace` keeps the wall clock (09:00 stays 09:00) and
   only labels it; `astimezone` would *move* it. Also check the gap: a wall time that was skipped
   does not survive the round trip local -> UTC -> local, so compare the naive parts and raise
   `ValueError` when they differ. A repeated time passes the round trip with `fold=0`, which is the
   first occurrence, as the docstring asks.
2. **`to_utc_iso` was right only by luck.** `naive.astimezone(...)` reads a naive time as the
   *computer's* zone. On a laptop in Kolkata the Kolkata ward looks fine; on a server running in
   UTC every ward is wrong. With bug 1 fixed, this function is correct.
3. **`shift_hours` subtracted wall clocks.** Even with aware datetimes, if both share the same
   `tzinfo` Python subtracts wall clock from wall clock, so 22:00 -> 06:00 is always 8 hours.
   Converting both to UTC first gives the real 7 or 9 hours on the nights the clocks change.
4. **`is_overdue` threw the zones away** to get rid of a `TypeError`. That `TypeError` was Python
   protecting you. Aware datetimes compare correctly with each other in any zones (Python
   converts both to UTC), so compare them directly, and refuse naive values with `ValueError`.

## Code

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FMT = "%Y-%m-%d %H:%M"
UTC = timezone.utc


def parse_local(text: str, zone: str) -> datetime:
    naive = datetime.strptime(text, FMT)
    tz = ZoneInfo(zone)
    local = naive.replace(tzinfo=tz)              # attach the zone: same wall time, now aware
    back = local.astimezone(UTC).astimezone(tz)    # a skipped time comes back different
    if back.replace(tzinfo=None) != naive:
        raise ValueError(f"{text} does not exist in {zone}: the clocks jumped over it")
    return local


def to_utc_iso(text: str, zone: str) -> str:
    return parse_local(text, zone).astimezone(UTC).isoformat()


def shift_hours(start_text: str, end_text: str, zone: str) -> float:
    start = parse_local(start_text, zone).astimezone(UTC)
    end = parse_local(end_text, zone).astimezone(UTC)
    return (end - start).total_seconds() / 3600


def is_overdue(due_iso: str, now: datetime) -> bool:
    due = datetime.fromisoformat(due_iso)
    if due.tzinfo is None or now.tzinfo is None:
        raise ValueError("both times must be aware (have a UTC offset)")
    return now > due
```

## Complexity

All O(1). `ZoneInfo(zone)` is cached, so calling it on every parse is cheap.

## Another way

Many teams turn every time into UTC at the moment it enters the program (`parse_local(...).astimezone(UTC)`)
and only ever store and compute with UTC values; local time is used only for input and display.
Then `shift_hours` cannot make the wall-clock mistake at all. For the gap check, another test is
`local.utcoffset()` versus `local.replace(fold=1).utcoffset()`: they differ for both skipped and
repeated times, and for a skipped time the round trip changes the wall clock.
