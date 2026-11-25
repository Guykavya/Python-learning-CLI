# `safe_merge`

Chapter section 14.1. Write the chapter's `safe_merge` yourself: a merge that **checks itself** and leaves a record
of what happened, so that a wrong join stops the analysis instead of quietly changing the numbers.

```text
safe_merge(left, right, on, how="left", validate="m:1", measure=None, name="",
           expect_same_rows=True, ledger=None)
```

1. Merge `left` with `right` on `on` (a column name or a list of names) with the given `how` and `validate`
   (pandas raises `pandas.errors.MergeError` when the relationship is wrong; let it through).
2. Build a **record** (a dict) with these keys:

   | key | value |
   |---|---|
   | `step` | `name`, or `f"merge on {keys}"` when `name` is empty (`keys` = the list of key columns) |
   | `left_rows`, `right_rows`, `result_rows` | the three row counts |
   | `unmatched_left` | number of result rows that came from `left` only (no partner in `right`) |
   | `unmatched_keys` | the sorted list of **distinct, non-missing** keys of those rows (for several key columns: tuples) |
   | `null_keys_left` | number of `left` rows with a missing value in any key column |
   | `measure_before`, `measure_after` | only when `measure` is given: the total of that column of `left`, and of the result, each rounded to 2 decimals |

   If `ledger` is a list, append the record to it **before** the checks below, so a failed step leaves evidence.
3. Two guards, each raising `AssertionError` with a message that starts with the step name:
   - when `how == "left"` and `expect_same_rows`: the result must have as many rows as `left`, message
     `"<step>: row count changed <before> -> <after>"`;
   - when `measure` is given (for any `how`): the totals before and after must differ by less than 0.01, message
     `"<step>: <measure> total changed <before> -> <after>"`.
4. Return the merged frame (without any helper column). Do not change the inputs.

(The chapter's version checks the measure only for a left join and writes to a global `LEDGER`; here the measure is
checked for every join, so an inner join that loses money is caught too, and the ledger is passed in.)

## Example

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3], "customer_id": ["C1", "C9", "C1"]})
customers = pd.DataFrame({"customer_id": ["C1", "C2"], "segment": ["retail", "premium"]})
ledger = []
out = safe_merge(orders, customers, on="customer_id", name="orders + customers", ledger=ledger)
print(len(out), out["segment"].tolist())
print(ledger[0])
```
```text
3 ['retail', nan, 'retail']
{'step': 'orders + customers', 'left_rows': 3, 'right_rows': 2, 'result_rows': 3, 'unmatched_left': 1, 'unmatched_keys': ['C9'], 'null_keys_left': 0}
```
