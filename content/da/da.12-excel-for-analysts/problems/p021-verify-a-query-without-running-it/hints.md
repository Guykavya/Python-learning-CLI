## Hint 1

Which pandas selector gives the numeric columns? Build the dict in the order of the statement so the comparison order is predictable. For the comparison, which structure lets you ask "is this key in `b`" and compare the values?

## Hint 2

```text
fp = {"rows": len(df), "columns": list(df.columns)}
for c in df.select_dtypes("number").columns: fp[f"sum({c})"] = round(float(df[c].sum()), 4)
for c in df.columns: fp[f"blank({c})"] = int(df[c].isna().sum())
for k in keys: fp[f"distinct({k})"] = int(df[k].nunique())
```
