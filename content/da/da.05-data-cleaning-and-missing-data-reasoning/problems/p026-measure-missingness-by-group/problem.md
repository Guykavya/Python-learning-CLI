# Measure missingness by group

Chapter sections 7.4 and 8.4. The first test for "does missingness depend on something I can see?" is a **profile**:
the share of missing values of one column inside each group of another column. A flat profile suggests MCAR; a clear
slope suggests MAR.

Write `missing_profile(df, by, col)`:

- `by` is the grouping column (a name), `col` the column whose missing values you measure.
- Return a **new** frame with one row per value of `by` and the columns `by` (same name), `rows` (rows in the group,
  `int`), `missing` (rows where `col` is missing, `int`) and `rate` (`missing / rows`, a float from 0 to 1).
- Sort by `rate`, **largest first**; groups with the same rate are ordered by the `by` value, smallest first.
- A group with no missing values has `missing = 0` and `rate = 0.0`: it still appears.
- The index is `0, 1, 2, ...`. Rows whose `by` value is missing are ignored. Do not change `df`.

## Example

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"edu": [8, 8, 8, 12, 12, 16, 16, 16, 16],
                   "income": [np.nan, 1, np.nan, 2, np.nan, 3, 4, 5, 6]})
print(missing_profile(df, "edu", "income"))
```

```text
   edu  rows  missing      rate
0    8     3        2  0.666667
1   12     2        1  0.500000
2   16     4        0  0.000000
```
