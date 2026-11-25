## Approach

A bridge is a running sum with a check at the end. Build the lines while you add, and compare the final running total
with the expected end value **before** returning anything: a table that does not close is not a bridge, it is a
statement of what you do not yet understand, so the function raises and names the gap with its sign
(`running - end`). The sign format `{change:+d}` writes `+29`, `-20` and `+0`.

## Code

```python
def bridge(start_label, start_value, steps, end_label, end_value):
    lines = ["step | change | running | check", " | ".join([start_label, "", str(start_value), ""]).rstrip()]
    running = start_value
    for label, change in steps:
        running += change
        lines.append(" | ".join([label, f"{change:+d}", str(running), ""]).rstrip())
    gap = running - end_value
    if gap != 0:
        raise ValueError(f"UNEXPLAINED {gap:+d}: bridge from {start_label} does not reach {end_label}")
    lines.append(" | ".join([f"= {end_label}", "", str(end_value), "OK"]))
    return "\n".join(lines)
```

## Complexity

O(s) for s steps: one pass, one string per line.

## Another way

The chapter builds the same table as a DataFrame (`cumsum` for the running column) and writes `UNEXPLAINED` into the
check column instead of raising. Raising is better in a pipeline that must stop; a printed `UNEXPLAINED +3` is better
in a report that must show what is still open. You can offer both with a parameter `strict=True`.
