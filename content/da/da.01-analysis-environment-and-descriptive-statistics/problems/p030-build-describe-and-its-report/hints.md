## Hint 1

Build `describe` first and check each number against `statistics` on a short list. Then `report` is only formatting plus one comparison. Where will the `None`s be removed, and how will you count them?

## Hint 2

```text
data = [v for v in values if v is not None]; missing = len(values) - len(data); empty -> ValueError
quartiles: n == 1 -> (value, value); else statistics.quantiles(data, n=4, method="inclusive")
sd: stdev if n > 1 else None;   skew_hint: (mean - median) / pstdev, 0.0 if pstdev == 0
report: s = describe(...); format six lines exactly as listed; one if/else for the advice
```
