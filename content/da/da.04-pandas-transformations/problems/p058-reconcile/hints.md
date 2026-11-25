## Hint 1

Turn `parts` into a Series so that a dict, a list and a Series all work the same, then sum it. Why does
`round(0.9999999999999999 - 1.0, 2)` print `-0.0`, and what tiny addition turns `-0.0` into `0.0`?

## Hint 2

```text
s = pd.Series(parts).sum()
diff = round(float(s - total), 2) + 0.0          (-0.0 + 0.0 is 0.0)
ok = abs(diff) <= tol
if strict and not ok:
    raise ValueError(f"{label}: parts={s:,.2f} total={total:,.2f} diff={diff:,.2f}")
return bool(ok), diff
```
