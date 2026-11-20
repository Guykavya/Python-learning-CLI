## Approach

Parse each field into a set of allowed values, then walk forward one day at a time and try the allowed hours and minutes in order. The full code is in `reference.py`; the two subtle parts:

```python
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
                end = high
        if not (low <= start <= end <= high):
            raise ValueError(f"bad {name} field {text!r}: values must be within {low}-{high}")
        values.update(range(start, end + 1, step))
    return values


def _day_matches(self, d):
    dom_ok = d.day in self.days
    dow_ok = (d.weekday() + 1) % 7 in self.weekdays
    if self.day_restricted and self.weekday_restricted:
        return dom_ok or dow_ok
    return dom_ok and dow_ok
```

## Complexity

Parsing is O(values in the field). `next_after` checks at most 1,830 days, and on a matching day at most 24 x 60 candidates, so it is fast enough for a scheduler that asks once a minute. A smarter version jumps straight to the next allowed month, day, hour and minute.

## Another way

Use a library (`croniter`, or the scheduler's own parser) in production. They also handle names (`MON`, `JAN`), `@daily` shortcuts and time zones. Time zones are the hard part: problem p028 shows what happens to a local 01:30 on a daylight-saving night.
