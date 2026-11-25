# Count values, including gaps

Chapter sections 5.3 and 11.1. `value_counts()` hides missing values unless you ask for them. A frequency table with the gaps
included tells you how much of the column you can actually trust.

Write `category_counts(s)` for a text Series. It returns a DataFrame with the columns `label`, `count`, `share`, one row
per distinct value:

- missing values appear as one row with the label `"(missing)"`;
- `share` is `count / len(s)` (missing values are part of the length);
- rows are ordered by `count` descending, and ties by `label` ascending (alphabetical);
- the index is `0, 1, 2, ...`.

The input is not changed.

## Example

```python
s = pd.Series(["Pune", "Agra", None, "Pune", "Delhi", "Agra", "Pune", None])
category_counts(s)
#      label  count  share
# 0       Pune      3  0.375
# 1  (missing)      2  0.250
# 2       Agra      2  0.250
# 3      Delhi      1  0.125
```
