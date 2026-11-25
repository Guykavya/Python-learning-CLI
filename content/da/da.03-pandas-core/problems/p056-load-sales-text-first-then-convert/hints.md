## Hint 1

Four small converters, one per group, each returning a Series with missing where it cannot decide: they are the helpers of section 18.2 (`to_money`, `to_date`, `to_bool`) plus an integer one. Which `to_numeric` argument turns unparseable text into missing instead of raising? And how do you make `2.5` missing for the integer group, not `2`?

## Hint 2

```text
raw = pd.read_csv(path, dtype="str", encoding="utf-8")
losses = {}
for each (columns, converter) pair:
    for c in columns:
        before = df[c]                          # the raw text
        df[c]  = converter(before)
        losses[c] = (before is not missing AND df[c] is missing).sum()
integers: num = to_numeric(text, errors="coerce"); num = num.where(num % 1 == 0); then .astype("Int64")
```
Dates: start from `NaT` and `fillna` with the result of each format in turn.
