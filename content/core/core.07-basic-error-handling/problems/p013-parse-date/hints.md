## Hint 1

Write the four checks as four separate steps, each ending in `raise` when it fails. Which
step needs `try`, and which are plain `if` tests?

## Hint 2

`[len(p) for p in parts]` gives the lengths in one list you can compare with `[4, 2, 2]`. Check
the number of parts first, or this comparison will just be false (which is also fine).

## Hint 3

```
parts = text.strip().split("-")
if wrong shape: raise ValueError(SHAPE message)
try:
    year, month, day = int(...), int(...), int(...)
except ValueError:
    raise ValueError(DIGITS message) from None
if month not in 1..12: raise ...
last = DAYS[month - 1], or 29 for February in a leap year
if day not in 1..last: raise ...
return year, month, day
```
