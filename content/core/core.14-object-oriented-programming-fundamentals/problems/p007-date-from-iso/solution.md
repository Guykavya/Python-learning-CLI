## Approach

Three kinds of method meet in one class (chapter section 6):

- `iso` is a normal method: it needs the object (`self`).
- `is_leap` needs no object and no class: just a year. A `staticmethod` keeps it inside the class,
  where it belongs, without a useless `self`.
- `from_iso` builds a new object, so it needs the **class**, not an object. A `classmethod` gets the
  class as `cls`. It only checks and splits the text, then hands the numbers to `cls(...)`, so the
  normal `__init__` still does all the date checks. There is one place for the rules, not two.

Returning `cls(...)` instead of `SimpleDate(...)` means `MyDate.from_iso(...)` builds a `MyDate`.

## Code

```python
MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


class SimpleDate:
    def __init__(self, year, month, day):
        if not 1 <= month <= 12:
            raise ValueError("month must be 1-12")
        if not 1 <= day <= SimpleDate.days_in_month(year, month):
            raise ValueError("bad day")
        self.year = year
        self.month = month
        self.day = day

    @staticmethod
    def is_leap(year):
        return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

    @staticmethod
    def days_in_month(year, month):
        if month == 2 and SimpleDate.is_leap(year):
            return 29
        return MONTH_DAYS[month - 1]

    @classmethod
    def from_iso(cls, text):
        parts = text.split("-")
        if (
            len(parts) != 3
            or [len(p) for p in parts] != [4, 2, 2]
            or not all(p.isdigit() for p in parts)
        ):
            raise ValueError("expected YYYY-MM-DD")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

    def iso(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
```

The month check must come before `days_in_month`, or `MONTH_DAYS[month - 1]` would crash (month 13)
or quietly use the wrong month (month 0 gives `MONTH_DAYS[-1]`, December).

## Complexity

O(1) for every method; the text has a fixed length.

## Another way

The standard library already has this: `datetime.date.fromisoformat("2024-03-05")` is a
classmethod alternative constructor, and `calendar.isleap(2024)` is the leap-year rule. Writing your
own once shows you how such constructors are built.
