## Approach

Keep the two operations apart:

| operation | method | what stays the same |
|---|---|---|
| attach a zone to a naive time | `naive.replace(tzinfo=ZoneInfo(zone))` | the clock reading |
| convert an aware time | `aware.astimezone(ZoneInfo(zone))` | the instant |

`to_utc` attaches first (the clock reading `09:30` belongs to Kolkata), then converts to UTC.
`utc_to_local` only converts. `ZoneInfo` knows the full history of each zone's rules, so the
same zone gives UTC+0 in January and UTC+1 in July for London, and the switch happens at the right
moment (01:00 UTC on 30 March 2025).

Every function checks its input first. Without the checks, the mistakes are silent:
`naive.astimezone(...)` uses the computer's own zone, and `naive == aware` is simply `False`.

Two aware datetimes compare by instant, whatever their zones, so `same_instant` is `a == b`
after the checks.

## Code

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def is_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.utcoffset() is not None


def to_utc(naive_local: datetime, zone: str) -> datetime:
    if is_aware(naive_local):
        raise ValueError("to_utc expects a naive wall-clock time")
    return naive_local.replace(tzinfo=ZoneInfo(zone)).astimezone(timezone.utc)


def utc_to_local(moment: datetime, zone: str) -> datetime:
    if not is_aware(moment):
        raise ValueError("utc_to_local expects an aware datetime")
    return moment.astimezone(ZoneInfo(zone))


def same_instant(a: datetime, b: datetime) -> bool:
    if not (is_aware(a) and is_aware(b)):
        raise ValueError("cannot compare instants of naive datetimes")
    return a == b
```

## Complexity

O(1) per call. `ZoneInfo(zone)` caches each zone after the first load.

## Another way

`datetime(2025, 3, 14, 9, 30, tzinfo=ZoneInfo("Asia/Kolkata"))` builds an aware time directly; use
it when you create the datetime yourself. For a zone with a fixed offset forever (like UTC, or
"UTC+5:30" in a data file), `timezone(timedelta(hours=5, minutes=30))` works without the IANA
database, but it does not know about summer time, so never use a fixed offset for a place like
London or New York. (Wall times that fall into a DST gap or overlap are the topic of the next
trace problem.)
