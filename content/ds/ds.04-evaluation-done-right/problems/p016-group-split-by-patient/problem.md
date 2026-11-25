# Group split by patient

Chapter section 6. When one patient has many visits, a random row split puts the same patient in both training and test, and the model recognises the patient instead of learning about the disease. Split by **group** instead.

Write `group_split(df, group_col, test_frac, seed)` returning `(train_idx, test_idx)`: two **sorted** NumPy arrays of row **positions**, made with `GroupShuffleSplit(n_splits=1, test_size=test_frac, random_state=seed)` and the column `group_col` as the groups.

## Example

```text
df: 80 patients x 15 visits;  group_split(df, "patient_id", 0.25, 0)
-> about 300 test rows from 20 patients; no patient on both sides
```
