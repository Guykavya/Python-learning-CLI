# Stack monthly files

Chapter section 7.3. The shop exports one sales file per month. You receive them already read into a dictionary
`{"2025-01": frame, "2025-02": frame, ...}` and must stack them into one table.

Write `stack_months(frames)`:

- the result has one row for every row of every frame, the frames in the order of the dictionary;
- a new **first** column `month` holds the dictionary key of the frame each row came from;
- after `month`, the columns are in the order they first appear (the first frame's columns, then any new column of a
  later frame);
- the index is fresh: `0, 1, 2, ...`;
- a column that exists in only some frames is missing (`NaN`) in the rows of the others. Do not drop it and do not fill it.

Call `pd.concat` once (not inside a loop). Do not change the input frames.

## Example

```python
import pandas as pd

frames = {
    "2025-01": pd.DataFrame({"order_id": [1, 2], "amount": [10.0, 20.0]}),
    "2025-02": pd.DataFrame({"order_id": [3], "amount": [5.0], "coupon": ["NEW"]}),
}
out = stack_months(frames)
print(list(out.columns))
print(out["month"].tolist(), out.index.tolist())
print(out["coupon"].tolist())
```
```text
['month', 'order_id', 'amount', 'coupon']
['2025-01', '2025-01', '2025-02'] [0, 1, 2]
[nan, nan, 'NEW']
```
