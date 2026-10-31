## Hint 1

`(b - a).days` is an int that may be negative; `abs()` fixes that. For business days, step one calendar day at a time (`timedelta(days=1)` or `-1`) and count a step only when the new day's `weekday()` is below 5. When do you stop?

## Hint 2

Age: start with `today.year - birth.year`, then subtract 1 if this year's birthday has not happened yet. "Not yet" is a comparison of `(month, day)` tuples: `(today.month, today.day) < (birth.month, birth.day)`. Check 29 February: on 28 Feb 2025 the tuple `(2, 28)` is smaller than `(2, 29)`, so not yet; on 1 March `(3, 1)` is not smaller, so the birthday has passed. That is exactly the rule.

For the duration: a timedelta stores `days`, `seconds` (0..86399) and `microseconds`. `divmod(td.seconds, 3600)` splits off the hours.

## Hint 3

```
days_between(a, b): return abs((b - a).days)

add_business_days(start, n):
    step = 1 if n >= 0 else -1
    day, left = start, abs(n)
    while left > 0:
        day += timedelta(days=step)
        if day.weekday() < 5: left -= 1
    return day

age_on(birth, today):
    years = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day): years -= 1
    return years

format_duration(td):
    if td < timedelta(0): raise ValueError
    h, rest = divmod(td.seconds, 3600); m, s = divmod(rest, 60)
    return f"{td.days}d {h:02d}:{m:02d}:{s:02d}"
```
