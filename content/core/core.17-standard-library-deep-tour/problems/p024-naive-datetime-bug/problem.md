# Fix: the naive-datetime bugs in a shift log

`starter.py` is a small module from a hospital that has wards in London, New York and Kolkata.
Every function **runs without an error**, and on most days it even gives the right answer. Then
users report:

- "Night-shift pay is wrong twice a year." (Some nights are paid 8 hours when they were 7 or 9.)
- "The UTC times in the export are wrong for some wards." (Right on one laptop, wrong on the server.)
- "The overdue list is wrong in the Kolkata office."
- "You can enter a shift starting at 01:30 on 31 March in London. That time never happened."

Copy `starter.py` to `solution.py` and fix it. Keep the four function names and their parameters.
Read the docstrings: they say what each function *should* do.

| Function | Must do |
|---|---|
| `parse_local(text, zone)` | Parse `"YYYY-MM-DD HH:MM"` as a wall-clock time in `zone` and return an **aware** `datetime` whose `tzinfo` is `ZoneInfo(zone)`. A time skipped by the clocks going forward raises `ValueError`. A repeated time (clocks going back) means the first one. |
| `to_utc_iso(text, zone)` | The same moment in UTC, as `isoformat()`: `"2024-07-01T03:30:00+00:00"`. Must give the same answer on every computer. |
| `shift_hours(start_text, end_text, zone)` | The hours that **really** passed, as a `float`. |
| `is_overdue(due_iso, now)` | `True` if `now` is strictly after the due moment. A naive `now` or a due time without an offset raises `ValueError`. |

There are several separate bugs, and fixing the first one does **not** fix the others. In
particular, after `parse_local` returns aware datetimes, `shift_hours` is *still* wrong. Why?

**Example**

```python
to_utc_iso("2024-07-01 09:00", "Asia/Kolkata")                       # '2024-07-01T03:30:00+00:00'
shift_hours("2024-10-26 22:00", "2024-10-27 06:00", "Europe/London")  # 9.0  (clocks went back)
shift_hours("2024-03-30 22:00", "2024-03-31 06:00", "Europe/London")  # 7.0  (clocks went forward)
is_overdue("2024-05-01T12:00:00+00:00",
           datetime(2024, 5, 1, 15, 0, tzinfo=ZoneInfo("Asia/Kolkata")))  # False: that is 09:30 UTC
parse_local("2024-03-31 01:30", "Europe/London")                     # ValueError
```

London's clocks: forward 01:00 -> 02:00 on 31 March 2024, back 02:00 -> 01:00 on 27 October 2024.
New York's: forward 02:00 -> 03:00 on 10 March 2024, back 02:00 -> 01:00 on 3 November 2024.

(On Windows, time-zone data needs `.venv/Scripts/python -m pip install tzdata`.)
