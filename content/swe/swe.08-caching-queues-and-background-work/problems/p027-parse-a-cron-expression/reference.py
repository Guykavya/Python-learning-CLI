from datetime import datetime, timedelta

FIELDS = [("minute", 0, 59), ("hour", 0, 23), ("day", 1, 31), ("month", 1, 12), ("weekday", 0, 6)]


def _number(text, name):
    if not text.isdigit():
        raise ValueError(f"bad {name} field: {text!r} is not a number")
    return int(text)


def parse_field(text, low, high, name="field"):
    values = set()
    for part in text.split(","):
        step = 1
        if "/" in part:
            part, step_text = part.split("/", 1)
            step = _number(step_text, name)
            if step < 1:
                raise ValueError(f"bad {name} field {text!r}: step must be at least 1")
        if part == "*":
            start, end = low, high
        elif "-" in part:
            a, b = part.split("-", 1)
            start, end = _number(a, name), _number(b, name)
        else:
            start = end = _number(part, name)
            if "/" in text:
                end = high                                   # "5/10" means from 5 to the end
        if not (low <= start <= end <= high):
            raise ValueError(f"bad {name} field {text!r}: values must be within {low}-{high}")
        values.update(range(start, end + 1, step))
    return values


class Cron:
    def __init__(self, expression):
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError(f"a cron expression has 5 fields, got {len(parts)}: {expression!r}")
        self.expression = expression
        self.minutes, self.hours, self.days, self.months, self.weekdays = (
            parse_field(text, low, high, name) for text, (name, low, high) in zip(parts, FIELDS))
        self.day_restricted, self.weekday_restricted = parts[2] != "*", parts[4] != "*"

    def _day_matches(self, d):
        dom_ok = d.day in self.days
        dow_ok = (d.weekday() + 1) % 7 in self.weekdays          # Python: Monday=0; cron: Sunday=0
        if self.day_restricted and self.weekday_restricted:
            return dom_ok or dow_ok
        return dom_ok and dow_ok

    def next_after(self, after):
        day = after.replace(hour=0, minute=0, second=0, microsecond=0)
        for _ in range(366 * 5):
            if day.month in self.months and self._day_matches(day):
                for hour in sorted(self.hours):
                    for minute in sorted(self.minutes):
                        candidate = day.replace(hour=hour, minute=minute)
                        if candidate > after:
                            return candidate
            day += timedelta(days=1)
        raise ValueError(f"no run time within 5 years for {self.expression!r}")

    def between(self, start, end):
        t = self.next_after(start)
        while t <= end:
            yield t
            t = self.next_after(t)
