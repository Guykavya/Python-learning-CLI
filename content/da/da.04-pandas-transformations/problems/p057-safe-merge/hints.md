## Hint 1

`merge(..., indicator=True)` adds a column `_merge` with `"both"`, `"left_only"` or `"right_only"`. Which rows tell you
the unmatched keys? Count the missing keys on `left` **before** merging. In which order must "append to the ledger"
and "check" happen so a failed step is still logged?

## Hint 2

```text
keys = [on] if on is a str else list(on)
null_keys = rows of left[keys] with any missing value
out = left.merge(right, on=on, how=how, validate=validate, indicator=True)
lonely = out[out["_merge"] == "left_only"][keys].dropna()
unmatched_keys = sorted(set(lonely[keys[0]].tolist()))          one key
               = sorted(set(lonely.itertuples(index=False, name=None)))   several keys
out = out.drop(columns="_merge")
record = {...}; add measure_before/after if measure; ledger.append(record) if ledger is not None
if how == "left" and expect_same_rows: assert len(out) == len(left), f"{step}: row count changed ..."
if measure: assert abs(after - before) < 0.01, f"{step}: {measure} total changed ..."
return out
```
