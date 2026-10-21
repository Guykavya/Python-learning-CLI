## Hint 1

How many times at most does the loop run? A `for` loop over `range(attempts)` stops by itself;
what goes **after** it?

## Hint 2

Inside the loop: one `try` around `float(text)` only. On `ValueError`, tell and `continue`. After
the `try`, an `if` for the range: `return` if good, tell if not.

## Hint 3

```
if attempts < 1: raise ValueError(...)
for _ in range(attempts):
    text = ask(prompt)
    try: value = float(text)
    except ValueError: tell(...); continue
    if low <= value <= high: return value
    tell(...)
raise ValueError(f"no valid answer after {attempts} attempts")
```
