# When does it run next?

Chapter sections 14.1 (cron expressions), 14.2 (time zones and daylight saving time) and "Try it: next run". The program uses the chapter's `Cron` class (`cron.py`, section 14.1, the same rules as problem p027) and `zoneinfo`.

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from cron import Cron

after = datetime(2026, 11, 7, 23, 50)                    # a Saturday
for number, expression in enumerate(["*/20 * * * *", "0 9 * * 1-5", "0 0 1 */3 *", "0 12 20 * 1"], start=1):
    print(f"{number}: {Cron(expression).next_after(after):%a %Y-%m-%d %H:%M}")

london = ZoneInfo("Europe/London")
spring = Cron("30 1 * * *").next_after(datetime(2026, 3, 28, 12, 0))      # clocks go 01:00 -> 02:00 on 29 March
as_utc = spring.replace(tzinfo=london).astimezone(timezone.utc)
print(f"5: {spring:%a %Y-%m-%d %H:%M} -> {as_utc:%H:%M} UTC -> {as_utc.astimezone(london):%H:%M} London")

autumn = datetime(2026, 10, 25, 1, 30)                   # clocks go 02:00 -> 01:00 on 25 October
first = autumn.replace(tzinfo=london, fold=0).astimezone(timezone.utc)
second = autumn.replace(tzinfo=london, fold=1).astimezone(timezone.utc)
print(f"6: {first:%H:%M} UTC and {second:%H:%M} UTC")
```

## Facts you need

- 2026-11-07 is a **Saturday**; 2027-01-01 is a **Friday**.
- `next_after` returns the first matching minute **strictly after** its argument. Cron weekdays: 0 = Sunday, 1 = Monday, ..., 6 = Saturday. When **both** day fields are restricted, a day matches if **either** one matches.
- `%a` prints the short English day name (`Mon`), `%H:%M` the time.
- **Europe/London** uses GMT (UTC+0) in winter and BST (UTC+1) in summer. On **Sunday 2026-03-29** the clocks jump from 01:00 to 02:00, so local times 01:00 to 01:59 do not exist that day. On **Sunday 2026-10-25** the clocks go back from 02:00 to 01:00, so 01:00 to 01:59 happen twice.
- A `datetime` with `fold=0` means the **first** of two possible readings of a local time (before the change); `fold=1` the second. For a time that does not exist, `fold=0` uses the offset that was valid **before** the jump. `astimezone` converts using that offset.

## What to write

The exact six lines of output.

## Example

Line 1: `*/20` allows minutes 0, 20, 40, and every hour and day. The first match strictly after Sat 23:50 is midnight: `1: Sun 2026-11-08 00:00`.

## After you answer

- A nightly job at `30 1 * * *` London time: on which date does it run at a surprising moment, and on which date could a naive scheduler run it twice?
- What is the chapter's rule of thumb for technical jobs?
