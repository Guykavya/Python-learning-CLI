## The bugs

| Starter line | Bug | Symptom |
|---|---|---|
| `for i in range(1, len(names)):` | skips position 0 | first student missing; marks lines shifted onto the wrong names |
| `if mark == "P" or "p":` | `or "p"` is always truthy | every mark counts as present |
| `present // days * 100` | floor division | percent is 0 or 100, never in between |
| `if percent <= 75:` | wrong boundary | exactly 75% marked LOW |
| `for ... else: print("All ...")` | loop has no `break` | the "all OK" line always prints |

## Fixed code

```python
names = input().split()
low = 0
for n, name in enumerate(names, start=1):
    marks = input().strip()
    present = 0
    for mark in marks:
        if mark in "Pp":
            present += 1
    days = len(marks)
    percent = present / days * 100
    line = f"{n}. {name}: {present}/{days} ({percent:.0f}%)"
    if percent < 75:
        line += " LOW"
        low += 1
    print(line)
if low == 0:
    print("All students at 75% or above")
else:
    print(f"Low attendance: {low}")
```

## Lessons

- `range(1, len(x))` is almost always a sign that `enumerate(x, start=1)` was meant.
- `x == a or b` never means "x is a or b".
- A loop `else` runs whenever there was no `break`. Without a `break` in the loop it always runs, so it was never the right tool here; a simple `if` after the loop is.
