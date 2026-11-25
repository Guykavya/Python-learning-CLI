# `safe_join`

Chapter section 13. A join can silently change the number of rows (fan-out, or a lost key). Two layers of protection
catch it: `validate=` checks the **relationship** (is the right side unique?) and a row-count check looks at the
**outcome** (did the left table keep its rows?).

Write `safe_join(left, right, on, how="left", validate="m:1", label="")`.

- Merge with `left.merge(right, on=on, how=how, validate=validate)`. Pandas raises its own `MergeError` when the
  relationship you declared does not hold: let it escape.
- When `how == "left"`, a left join must keep **every left row exactly once** in the usual case. Compare the row counts of
  `left` and the result; if they differ raise `AssertionError` with the text
  `"<label>: rows changed <before> -> <after> (fan-out or a lost key?)"`. When `label` is empty, use `"join on <on>"`
  as the label (for example `join on job_id`; `<on>` is written as given, so a list is written as `['a', 'b']`).
- For other values of `how` (`"inner"`, ...) only the `validate` check applies: the number of rows may change on purpose.
- Return the merged DataFrame. Do not change `left` or `right`.

## Example

```python
import pandas as pd

jobs = pd.DataFrame({"job_id": [1, 2, 3], "customer_id": [10, 10, 11]})
customers = pd.DataFrame({"customer_id": [10, 11], "city": ["Pune", "Delhi"]})
payments = pd.DataFrame({"job_id": [1, 1, 2], "amount": [400, 600, 500]})

print(len(safe_join(jobs, customers, on="customer_id", label="jobs + customers")))
try:
    safe_join(jobs, payments, on="job_id", validate="1:m", label="jobs + payments")
except AssertionError as e:
    print("AssertionError:", e)
```

```text
3
AssertionError: jobs + payments: rows changed 3 -> 4 (fan-out or a lost key?)
```
