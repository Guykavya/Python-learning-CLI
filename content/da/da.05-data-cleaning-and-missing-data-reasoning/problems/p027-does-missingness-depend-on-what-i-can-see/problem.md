# Does missingness depend on what I can see?

Chapter section 8.4. You cannot prove MCAR, but you can look for **signs of MAR**: compare another column between the
rows where a value is missing and the rows where it is present. If the two groups look alike, missingness shows no link
to that column. A big gap means the missingness depends on it.

Write `missingness_gap(df, col, other)`:

- `col` is the column with missing values, `other` a numeric column that has no missing values.
- Return a dict with three floats:
  - `"missing_mean"`: the mean of `other` over the rows where `col` is **missing**;
  - `"present_mean"`: the mean of `other` over the rows where `col` is **present**;
  - `"gap"`: `missing_mean - present_mean`.
- If one of the two groups is empty, its mean (and the gap) is `NaN`. Do not change `df`.

The tests also simulate data where the answer is known (the `make_population` of the chapter, with incomes hidden by a
coin flip, or twice as often for people under 40), and check that the gap is **large for the column that drives the
missingness and near zero for a column that does not**. Think about what that says about the reading of a gap.

## Example

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"income": [10.0, np.nan, 30.0, np.nan, 50.0],
                   "age":    [25, 22, 40, 24, 45]})
print(missingness_gap(df, "income", "age"))
```

```text
{'missing_mean': 23.0, 'present_mean': 36.666666666666664, 'gap': -13.666666666666664}
```

The two missing incomes belong to people aged 22 and 24 (mean 23); the three present ones to 25, 40, 45 (mean 36.67).
