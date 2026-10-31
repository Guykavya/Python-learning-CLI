# datetime: parse and format dates

Dates arrive as text in many shapes: `2025-03-14 09:05:30` in a log, `03/14/2025` from a US
form, `2025-03-14T09:05:30` from an API. **Parse** them into `date`/`datetime` objects as soon as
they enter your program, work with the objects, and **format** them back to text only for output.

- `datetime.strptime(text, fmt)` parses ("string parse time"); a mismatch raises `ValueError`.
- `obj.strftime(fmt)` or an f-string `f"{obj:fmt}"` formats.
- `datetime.fromisoformat(text)` and `obj.isoformat()` handle the ISO 8601 standard format.

Common codes: `%Y` year (4 digits), `%m` month 01-12, `%d` day 01-31, `%H` hour 00-23, `%M` minute,
`%S` second, `%a` short weekday (`Fri`), `%b` short month (`Mar`).

Write four functions in `solution.py`:

1. `parse_log_stamp(text: str) -> datetime`: parse `"2025-03-14 09:05:30"`.
2. `parse_us_date(text: str) -> date`: parse `"03/14/2025"` (month/day/year) and return a
   `date` (not a `datetime`).
3. `to_iso(dt: datetime) -> str`: `"2025-03-14T09:05:30"`.
4. `pretty(dt: datetime) -> str`: `"Fri 14 Mar 2025, 09:05"`. The **day has no leading zero**:
   the 4th is `"Tue 4 Mar 2025, 09:05"`. The hour and minute keep two digits.

Text that does not match the expected format must raise `ValueError` (the parsers do this for you).

**Example**

```python
parse_log_stamp("2025-03-14 09:05:30")      # datetime(2025, 3, 14, 9, 5, 30)
parse_us_date("03/14/2025")                 # date(2025, 3, 14)
to_iso(datetime(2025, 3, 14, 9, 5, 30))     # '2025-03-14T09:05:30'
pretty(datetime(2025, 3, 4, 9, 5))          # 'Tue 4 Mar 2025, 09:05'
```
