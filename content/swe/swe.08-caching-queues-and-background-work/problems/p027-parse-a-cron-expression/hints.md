## Hint 1

Parse one part at a time. First split off the step (`/n`); then the rest is `*`, `a-b` or a single number, which gives a start and an end; then `range(start, end + 1, step)`. Where do `low`, `high` and the special case `5/10` come in? Which error checks can you do with one condition (`low <= start <= end <= high`)?

## Hint 2

```text
next_after(after):
    day = midnight of after's date
    repeat for 5 years of days:
        if day.month allowed and day matches (the OR rule when both day fields are restricted):
            for hour in sorted(hours): for minute in sorted(minutes):
                t = day at hour:minute; if t > after: return t
        day += 1 day
    raise ValueError
```

Convert any non-number with your own check (`text.isdigit()`) so the error message can name the field.
