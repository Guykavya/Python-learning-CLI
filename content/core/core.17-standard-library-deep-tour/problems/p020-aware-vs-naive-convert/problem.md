# zoneinfo: aware vs naive, and converting zones

A **naive** `datetime` has no `tzinfo`: `datetime(2025, 7, 15, 12, 0)` is "12:00 somewhere".
An **aware** one knows its zone: `datetime(2025, 7, 15, 12, 0, tzinfo=ZoneInfo("Europe/London"))`
is one exact instant (11:00 UTC, because London is on summer time in July).

- `naive.replace(tzinfo=ZoneInfo(zone))` **attaches** a zone: same wall-clock time, now aware.
- `aware.astimezone(ZoneInfo(other))` **converts**: same instant, different wall-clock time.
- Calling `astimezone()` on a **naive** datetime does not fail: it silently assumes the naive time
  is in **your computer's** local zone. The same code then gives different answers on different
  machines. That is the bug to avoid here.

Time-zone rules (like summer time) come from the IANA database. On Windows it is not built in;
the `tzdata` package provides it (`.venv/Scripts/python -m pip install tzdata`).

Write in `solution.py` (import `ZoneInfo` from `zoneinfo` and `timezone` from `datetime`):

1. `is_aware(dt: datetime) -> bool`: `True` when `dt.tzinfo` is set **and** `dt.utcoffset()` is not `None`.
2. `to_utc(naive_local: datetime, zone: str) -> datetime`: the naive time is a wall-clock time in
   `zone` (for example `"Asia/Kolkata"`). Return the same instant as an aware datetime in UTC
   (`tzinfo=timezone.utc`). An already-aware input raises `ValueError`.
3. `utc_to_local(moment: datetime, zone: str) -> datetime`: convert an **aware** datetime to the
   wall-clock time in `zone` (the result's `tzinfo` is that `ZoneInfo`). A naive input raises `ValueError`.
4. `same_instant(a: datetime, b: datetime) -> bool`: do two aware datetimes describe the same
   moment? Either one naive: `ValueError`.

**Example**

```python
to_utc(datetime(2025, 3, 14, 9, 30), "Asia/Kolkata")
# datetime(2025, 3, 14, 4, 0, tzinfo=timezone.utc)          India is UTC+5:30

utc_to_local(datetime(2025, 7, 4, 13, 0, tzinfo=timezone.utc), "America/New_York")
# datetime(2025, 7, 4, 9, 0, tzinfo=ZoneInfo('America/New_York'))   EDT, UTC-4
```
