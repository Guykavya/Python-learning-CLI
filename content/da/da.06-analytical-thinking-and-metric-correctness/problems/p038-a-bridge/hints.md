## Hint 1

What do you need to remember while you walk through the steps, so that each line can show a running total? Where do you
check that the steps reach the end value, and what must happen if they do not? How do you print a number with its sign,
including `+0`?

## Hint 2

```text
lines = [header, start line]
running = start_value
for label, change in steps:
    running += change
    lines.append(join [label, f"{change:+d}", str(running), ""] with " | ", then rstrip)
gap = running - end_value
if gap != 0: raise ValueError(f"UNEXPLAINED {gap:+d}: bridge from {start_label} does not reach {end_label}")
lines.append(end line with "OK")
return "\n".join(lines)
```
