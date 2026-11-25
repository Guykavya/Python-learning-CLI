## Hint 1

All five parts live in the `.dt` accessor of section 13.3: `year`, `month`, `quarter`, `day_name()`, and `day_of_week` (Monday is 0). Which comparison on `day_of_week` marks Saturday and Sunday?

## Hint 2

```text
d   = df[col]
out = df.copy()
out["year"]       = d.dt.year
out["month"]      = d.dt.month
out["quarter"]    = d.dt.quarter
out["weekday"]    = d.dt.day_name()
out["is_weekend"] = d.dt.day_of_week >= 5      # Sat = 5, Sun = 6
return out
```
`NaT` gives missing parts, and `NaN >= 5` is `False`, which is exactly the rule for `is_weekend`.
