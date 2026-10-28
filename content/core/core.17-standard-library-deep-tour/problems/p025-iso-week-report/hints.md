## Hint 1

`date(2024, 12, 30).isocalendar()` returns a named tuple. Print it. Which field is the year you
need: `d.year` or the one inside the tuple? How do you write a week number `1` as `01` in an f-string?

## Hint 2

For `week_start`, split the key: `key.partition("-W")` gives `(year_text, "-W", week_text)`, and
the middle part is empty if `-W` is missing. Check the lengths, convert with `int()`, and let
`date.fromisocalendar(year, week, 1)` raise `ValueError` for a week that does not exist.

## Hint 3

```
totals = {}   days = {}        # key -> hours,  key -> set of dates
for text, hours in entries:
    d = date.fromisoformat(text); key = week_key(d)
    totals[key] += hours;  days[key].add(d)
for key in sorted(totals):
    monday = week_start(key); sunday = monday + 6 days
    line: f"{key} {monday}..{sunday}: {total:.1f} h on {n} day/days"
```
