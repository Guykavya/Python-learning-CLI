# Meeting times across time zones

A team has people in London, New York and Kolkata. You will write two helpers for planning a call.
Use `zoneinfo.ZoneInfo` for the zones; never hard-code offsets like "+5:30" or "-5", because
London and New York change their offsets twice a year (on **different** dates).

1. `show_in_zones(when, zones) -> list[str]`
   `when` is an **aware** `datetime` (in any zone). For each zone name in `zones`, in order, return
   a line `"<zone>: YYYY-MM-DD HH:MM <abbreviation>"` with the local date and time there.
   The abbreviation is `local.tzname()` (for example `GMT`, `BST`, `EST`, `EDT`, `IST`, `UTC`).
   If `when` is naive, raise `ValueError`.

2. `common_hours(day, zones, start_hour=9, end_hour=17) -> list[datetime]`
   Look at the 24 one-hour slots of the **UTC** day `day` (00:00-01:00 UTC, 01:00-02:00 UTC, ...,
   23:00-24:00 UTC). Return the starts of the slots that lie completely inside working hours in
   **every** zone: in each zone the slot must start at or after `start_hour:00` local time and end
   at or before `end_hour:00` local time. Return aware datetimes in UTC (`tzinfo=timezone.utc`), in order.
   Compare only the clock time (hour and minute); ignore weekends.

**Examples**

```python
from datetime import date, datetime, timezone

show_in_zones(datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc), ["Europe/London", "Asia/Kolkata"])
# ['Europe/London: 2024-03-15 14:00 GMT', 'Asia/Kolkata: 2024-03-15 19:30 IST']

[s.hour for s in common_hours(date(2024, 1, 15), ["Europe/London", "America/New_York"])]
# [14, 15, 16]
[s.hour for s in common_hours(date(2024, 3, 15), ["Europe/London", "America/New_York"])]
# [13, 14, 15, 16]     New York has moved its clocks, London has not yet
```

**Time-zone data**: Linux and macOS have it built in. On Windows run
`.venv/Scripts/python -m pip install tzdata` once; the tests tell you if it is missing.
