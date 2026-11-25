## Hint 1

What dtype name keeps integers when there are gaps? What does `astype` do when a value cannot be converted: does it round, or complain? Which exception would you like the caller to see, and what should its message contain?

## Hint 2

```text
out = df.copy()
for col in cols:
    try:    out[col] = out[col].astype("Int64")      # 2.0 -> 2, NaN -> <NA>, 2.5 -> error
    except (TypeError, ValueError):  raise ValueError("column <col> has non-integer values")
return out
```
