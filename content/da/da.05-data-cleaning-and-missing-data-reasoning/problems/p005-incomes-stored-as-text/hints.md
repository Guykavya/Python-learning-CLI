## Hint 1

Which values mean "missing" before any conversion starts? Which pieces must you remove, and in which order: does it
matter whether you remove the commas before or after the trailing `k`? What would be a safe way to decide whether the
rest is a number: try `float()` and catch errors, or check its shape with a pattern first?

## Hint 2

```text
for each value v:
    if v is missing: NaN
    t = strip + lower
    if t in {"", "n/a", "-999"}: NaN
    t = remove leading currency mark (a regex anchored at the start)
    t = remove trailing "/-"
    factor = 1000 if t ends with "k" (and cut the k) else 1
    t = remove commas
    if t does not look like digits[.digits]: NaN
    else float(t) * factor
```
A plain loop over the Series is fine; so is `str.replace(..., regex=True)` on the whole column plus `pd.to_numeric`.
