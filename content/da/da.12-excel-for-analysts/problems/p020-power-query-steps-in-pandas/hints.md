## Hint 1

Write one small function per step and a loop that picks the right one by name. What must you do first so that the caller's table is never changed?

## Hint 2

```text
out = df.copy()
for s in steps: name = s["step"]; if name == "trim": for c in s["columns"]: out[c] = out[c].str.strip() ...
unknown -> raise ValueError(f"unknown step: {name}")
filter_blanks: keep rows where out[col].notna() & (out[col] != "")
```
