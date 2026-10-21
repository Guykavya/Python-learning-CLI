## Approach

Split the problem by shape. One `match` recognises "time" or "time plus suffix". A second
`match` recognises two or three time parts. Range checks come after the shape is known.

## Code

```python
while True:
    line = input().strip()
    if line == "end":
        break
    valid = False
    match line.lower().split():
        case [time_text]:
            suffix = ""
        case [time_text, ("am" | "pm") as suffix]:
            pass
        case _:
            time_text = ""
            suffix = ""
    match time_text.split(":"):
        case [h, m]:
            s = "00"
        case [h, m, s]:
            pass
        case _:
            h = m = s = ""
    if (h.isdigit() and m.isdigit() and s.isdigit()
            and 1 <= len(h) <= 2 and len(m) == 2 and len(s) == 2):
        hour, minute, second = int(h), int(m), int(s)
        if suffix:
            hour_ok = 1 <= hour <= 12
            hour = hour % 12 + (12 if suffix == "pm" else 0)
        else:
            hour_ok = hour <= 23
        valid = hour_ok and minute < 60 and second < 60
    if valid:
        total = hour * 3600 + minute * 60 + second
        print(f"{hour:02d}:{minute:02d}:{second:02d} = {total} s")
    else:
        print(f"invalid: {line}")
```

## New pattern feature: `as`

`("am" | "pm") as suffix` matches either word **and** captures which one it was. It combines
an OR pattern with a capture.

## Why shape first, values second

Every check on values (digits, ranges) assumes the right number of parts. Matching the shape
first means the value checks never index something that is not there.

## The 12-hour rule

`hour % 12` turns 12 into 0 and leaves 1 to 11 alone. Adding 12 for `pm` gives 12 for
`12 pm` and 13 to 23 for the rest.
