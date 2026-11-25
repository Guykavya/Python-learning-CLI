## Hint 1

Which method gives a Boolean Series that is `True` where the value is one of a list? Which method keeps the values where
a condition is false and writes `NaN` where it is true (`mask`) and which one does the opposite (`where`)? What do you
have to copy so that the caller's frame stays as it was?

## Hint 2

```text
out = df.copy()
counts = {}
for col, values in codes.items():
    hit = out[col].isin(values)
    counts[col] = int(hit.sum())
    out[col] = out[col].mask(hit)
return out, counts
```
