## Approach

Three nets, from the cheapest to the most general. `validate=` lets pandas check the promised relationship before
anything else (a duplicated key on the "one" side raises `MergeError`). The row-count guard catches a fan-out when
`validate` was switched off, and the measure guard catches any change of money, including rows lost by an inner join.
`indicator=True` labels each result row with its origin, which gives the unmatched count and keys; the missing keys
are counted on `left` before the merge because a missing key can never be a real match. The record goes into the
ledger before the guards, so the evidence of a failed step stays in the log.

## Code

```python
import pandas as pd


def safe_merge(left, right, on, how="left", validate="m:1", measure=None, name="",
               expect_same_rows=True, ledger=None):
    keys = [on] if isinstance(on, str) else list(on)
    null_keys = int(left[keys].isna().any(axis=1).sum())
    out = left.merge(right, on=on, how=how, validate=validate, indicator=True)
    lonely = out.loc[out["_merge"] == "left_only", keys].dropna()
    if len(keys) == 1:
        unmatched_keys = sorted(set(lonely[keys[0]].tolist()))
    else:
        unmatched_keys = sorted(set(lonely.itertuples(index=False, name=None)))
    unmatched = int((out["_merge"] == "left_only").sum())
    out = out.drop(columns="_merge")
    step = name or f"merge on {keys}"
    record = {"step": step, "left_rows": len(left), "right_rows": len(right), "result_rows": len(out),
              "unmatched_left": unmatched, "unmatched_keys": unmatched_keys, "null_keys_left": null_keys}
    if measure is not None:
        record["measure_before"] = round(float(left[measure].sum()), 2)
        record["measure_after"] = round(float(out[measure].sum()), 2)
    if ledger is not None:
        ledger.append(record)
    if how == "left" and expect_same_rows:
        assert len(out) == len(left), f"{step}: row count changed {len(left)} -> {len(out)}"
    if measure is not None:
        before, after = record["measure_before"], record["measure_after"]
        assert abs(after - before) < 0.01, f"{step}: {measure} total changed {before} -> {after}"
    return out
```

## Complexity

The merge is O(n + m) with hashing; the extra checks are O(n) passes over the result. The cost is tiny compared with
the cost of a wrong total in a report.

## Another way

Keep the ledger as a list of dicts and show it with `pd.DataFrame(ledger).set_index("step")`, as the chapter does.
Some teams raise their own exception class (`class JoinCheckError(AssertionError)`) so a caller can catch exactly
these failures; `assert` statements are also removed when Python runs with `-O`, which is another reason to prefer
`if ...: raise` in production code.
