## Hint 1

For `show_in_zones`, one call does the conversion: `when.astimezone(ZoneInfo(name))`. How can you
tell that `when` is naive before you call it? (Look at `when.tzinfo`.) An f-string with a format
spec like `f"{local:%Y-%m-%d %H:%M}"` formats the date and time.

## Hint 2

For `common_hours`, build the first slot as an aware UTC datetime:
`datetime(day.year, day.month, day.day, tzinfo=timezone.utc)`. Each next slot is that plus
`timedelta(hours=h)`. For each slot and each zone, convert it and look at the local clock. Why is
checking only `local.hour` not enough for Kolkata?

## Hint 3

```
first = midnight UTC of day
for h in 0..23:
    slot = first + h hours
    ok = True
    for each zone:
        local = slot.astimezone(zone)
        m = local.hour * 60 + local.minute          # minutes since local midnight
        if m < start_hour*60 or m + 60 > end_hour*60: ok = False
    if ok: keep slot
```
