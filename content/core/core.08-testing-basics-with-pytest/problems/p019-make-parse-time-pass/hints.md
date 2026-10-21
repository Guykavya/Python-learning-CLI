## Hint 1

Which line of the specification does the **first** failing test cover? Fix only that and run again. That is the TDD loop.

## Hint 2

`text.split(":")` splits into parts. How many parts must a good text give? Which check comes before converting with `int`, and which `except` catches a bad number?

## Hint 3

```
parts = text.strip().split(":")
if len(parts) != 2: raise ValueError("expected H:MM")
try: hours = int(parts[0]); minutes = int(parts[1])
except ValueError: raise ValueError("hours and minutes must be whole numbers") from None
if minutes > 59 (or < 0): raise ValueError("minutes must be 0 to 59")
return hours * 60 + minutes
```
