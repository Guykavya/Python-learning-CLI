## Hint 1

Compute the revenue of every line first. Then decide, line by line, which of three groups it belongs to: code not found, region not matched (code fine), or fine. Why must a line with both faults be counted only once?

## Hint 2

```text
rev = float(units) * price * (1 - discount)
code_bad = str(code).upper() not in valid_codes
region_bad = str(region).lower() not in {r.lower() for r in regions}
cause1 = rev[code_bad].sum(); cause2 = rev[~code_bad & region_bad].sum()
grid = rev[~code_bad & ~region_bad].sum()
```
