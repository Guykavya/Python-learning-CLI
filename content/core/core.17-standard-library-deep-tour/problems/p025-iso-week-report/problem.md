# Weekly report by ISO week

Timesheets, sprint reports and invoices are often grouped by **ISO week**. The ISO 8601 rules:

- A week runs **Monday to Sunday**.
- Week 1 of a year is the week that contains that year's **first Thursday** (so it contains 4 January).
- So the first days of January can belong to the last week of the *previous* year, and the last
  days of December can belong to week 1 of the *next* year. Some years have 53 weeks.

`date.isocalendar()` gives `(year, week, weekday)` by these rules, where `year` is the
**ISO year**, which is not always `d.year`. `date.fromisocalendar(year, week, weekday)` goes back.

Write in `solution.py`:

1. `week_key(d: date) -> str`: `"YYYY-Www"`, ISO year and two-digit ISO week, like `"2025-W01"`.
2. `week_start(key: str) -> date`: the Monday of that week. A key not in the exact form
   `"YYYY-Www"` (four-digit year, `-W`, two-digit week) or a week that does not exist in that year
   (`"2024-W53"`, `"2025-W00"`) raises `ValueError`.
3. `weekly_report(entries) -> list[str]`: `entries` is a list of `(iso_date_text, hours)` such as
   `("2024-12-30", 2.5)`, in any order. Return one line per week, oldest week first:

   ```
   <key> <monday>..<sunday>: <total hours, 1 decimal> h on <n> day(s)
   ```

   where the dates are ISO (`2024-12-30`), and `n` is the number of **different** dates in that
   week (write `1 day`, `2 days`).

**Example**

```python
week_key(date(2024, 12, 30))     # '2025-W01'   (a Monday: week 1 of 2025 starts here)
week_key(date(2024, 12, 29))     # '2024-W52'
week_start("2025-W01")           # date(2024, 12, 30)

weekly_report([("2025-01-02", 3.0), ("2024-12-30", 2.5), ("2024-12-29", 1.0),
               ("2024-12-30", 1.5), ("2025-01-05", 4.0)])
# ['2024-W52 2024-12-23..2024-12-29: 1.0 h on 1 day',
#  '2025-W01 2024-12-30..2025-01-05: 11.0 h on 3 days']
```
