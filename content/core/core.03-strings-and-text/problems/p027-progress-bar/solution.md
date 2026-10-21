## Code

```python
done = int(input())
total = int(input())
filled = done * 20 // total
bar = "#" * filled + "-" * (20 - filled)
print(f"[{bar}] {done / total:.0%} ({done}/{total})")
```

## Why multiply before dividing

`done // total * 20` is 0 for every partial value, because `done // total` is 0 until everything is done. Multiplying first keeps the information.

## Rounding of the percent

`:.0%` rounds half to even, like `round()`. For example 1/8 is 12.5%, which shows as `12%`. The tests use the same rule, so just use the format spec.

## Another way

`"#" * filled` padded with `ljust(20, "-")` gives the same bar: `("#" * filled).ljust(20, "-")`.
