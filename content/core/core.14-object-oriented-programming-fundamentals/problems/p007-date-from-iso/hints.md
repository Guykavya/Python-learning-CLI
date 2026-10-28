## Hint 1

`from_iso` does two jobs: check and split the text, then call the normal constructor. Why should
it end with `return cls(year, month, day)` and not `return SimpleDate(year, month, day)`? Think about a
subclass `class MyDate(SimpleDate): pass` calling `MyDate.from_iso(...)`.

## Hint 2

`text.split("-")` gives a list of parts. You need exactly three parts, of lengths 4, 2, 2, and each
part must satisfy `part.isdigit()`. For the day check, a list of month lengths helps:
`[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]`, with February raised to 29 when `is_leap(year)`.

## Hint 3

```
class SimpleDate:
    def __init__(self, year, month, day):
        if not 1 <= month <= 12: raise ValueError("month must be 1-12")
        if not 1 <= day <= SimpleDate.days_in_month(year, month): raise ValueError("bad day")
        store year, month, day

    @staticmethod
    def is_leap(year):
        return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

    @staticmethod
    def days_in_month(year, month):
        ...

    @classmethod
    def from_iso(cls, text):
        parts = text.split("-")
        if not (3 parts, lengths 4, 2, 2, all digits): raise ValueError("expected YYYY-MM-DD")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

    def iso(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
```
