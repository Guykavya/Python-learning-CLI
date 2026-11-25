# Rename, drop, assign

Chapter section 14.1. A table exported from a spreadsheet has untidy column names (`" Order ID"`, `"Unit Price "`,
`"QTY"`) and helper columns that start with `TMP_`. Write `prepare(df)` that returns a **new** frame in which

1. every column name is **snake_case**: stripped, lower case, spaces replaced by `_` (`" Order ID"` becomes `order_id`);
2. every column whose new name starts with `tmp_` is dropped;
3. a column `revenue = qty * unit_price` is added at the end.

Write it as **one method chain** (`rename`, `drop` or `loc`, `assign`): no intermediate variables that you edit
afterwards. Row order and index stay the same, and the input frame is not changed.

## Example

```python
import pandas as pd

from solution import prepare

raw = pd.DataFrame({" Order ID": [1, 2], "Unit Price ": [250.0, 80.0], "QTY": [2, 5], "TMP_note": ["x", "y"]})
out = prepare(raw)
print(out.columns.tolist())
print(out["revenue"].tolist())
print(raw.columns.tolist())
```

```text
['order_id', 'unit_price', 'qty', 'revenue']
[500.0, 400.0]
[' Order ID', 'Unit Price ', 'QTY', 'TMP_note']
```
