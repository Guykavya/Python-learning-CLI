# A date with an alternative constructor

Dates often arrive as text like `"2024-03-05"` (the ISO format: year, month, day). A class can have
more than one way to be built: the normal `SimpleDate(2024, 3, 5)`, and an **alternative
constructor** `SimpleDate.from_iso("2024-03-05")` written as a `classmethod`. A helper that needs
neither an object nor the class, like "is this year a leap year?", can be a `staticmethod`.

Write a class `SimpleDate` in `solution.py`:

- `SimpleDate(year, month, day)` stores the three ints as attributes `year`, `month`, `day`.
  - If `month` is not 1 to 12, raise `ValueError("month must be 1-12")`.
  - If `day` is not between 1 and the number of days in that month, raise `ValueError("bad day")`.
    Months have 31 days, except April, June, September, November (30) and February (28, or 29 in a
    leap year).
- A **staticmethod** `is_leap(year)` returns `True` for leap years: divisible by 4, except years
  divisible by 100, unless also divisible by 400. So 2024 and 2000 are leap years; 1900 and 2023 are not.
- A **classmethod** `from_iso(text)` builds a date from `"YYYY-MM-DD"`. The text must be exactly
  4 digits, `-`, 2 digits, `-`, 2 digits; otherwise raise `ValueError("expected YYYY-MM-DD")`. It must
  return `cls(...)`, so a subclass gets an object of the subclass.
- `d.iso()` returns the date as `"YYYY-MM-DD"` text, with zeros in front where needed.

**Example**

```python
d = SimpleDate.from_iso("2024-03-05")
print(d.year, d.month, d.day)         # 2024 3 5
print(d.iso())                        # 2024-03-05
print(SimpleDate.is_leap(1900))       # False
print(SimpleDate(2024, 2, 29).iso())  # 2024-02-29
SimpleDate(2023, 2, 29)               # ValueError: bad day
SimpleDate.from_iso("2024/03/05")     # ValueError: expected YYYY-MM-DD
```
