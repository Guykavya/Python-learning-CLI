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
