## Approach

Keep every instant **aware**, and let `zoneinfo` decide the offset for each zone *on that date*.
`when.astimezone(ZoneInfo(name))` gives the same instant seen on a wall clock in that zone, with
the right abbreviation, so the formatting is just an f-string.

For the meeting slots, walk through the 24 UTC hours of the day. A slot is good if, in every
zone, it starts no earlier than `start_hour:00` and ends no later than `end_hour:00` local time.
Measuring the local time in minutes since midnight handles half-hour zones like Kolkata
(UTC+5:30): the 03:00 UTC slot starts at 08:30 there, which is too early, even though
`local.hour` for its *end* is 9.

The test for 15 March 2024 shows why offsets must not be hard-coded: the USA moves its clocks on
the second Sunday of March, the UK on the last Sunday of March, so for about three weeks the gap
between London and New York is 4 hours instead of 5.

## Code

```python
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def show_in_zones(when: datetime, zones: list[str]) -> list[str]:
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError("when must be an aware datetime (it has no time zone)")
    lines = []
    for name in zones:
        local = when.astimezone(ZoneInfo(name))
        lines.append(f"{name}: {local:%Y-%m-%d %H:%M} {local.tzname()}")
    return lines


def common_hours(day: date, zones: list[str], start_hour: int = 9, end_hour: int = 17) -> list[datetime]:
    tzs = [ZoneInfo(name) for name in zones]
    first = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    result = []
    for h in range(24):
        slot = first + timedelta(hours=h)
        ok = True
        for tz in tzs:
            local = slot.astimezone(tz)
            minutes = local.hour * 60 + local.minute
            if minutes < start_hour * 60 or minutes + 60 > end_hour * 60:
                ok = False
                break
        if ok:
            result.append(slot)
    return result
```

## Complexity

`show_in_zones` is O(z) for z zones. `common_hours` is O(24 * z). `ZoneInfo(name)` is cached by
the module, so creating it again is cheap.

## Another way

Instead of testing 24 slots, compute each zone's working window as a pair of UTC instants
(`datetime(..., 9, tzinfo=zone).astimezone(timezone.utc)` and the same for 17:00) and intersect
the windows with `max(starts)` and `min(ends)`. That is faster for many zones, but you must be
careful about which local day to use for zones far from UTC; the slot loop avoids that problem.
