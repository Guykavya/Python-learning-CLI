# Exact duplicates

Chapter section 5.2. `duplicated()` is `True` for every row that repeats an **earlier** row. Two rows are exact
duplicates only if **every column** is equal, so `Pune` and `pune` are *different* values here: normalising the text is
a different step, done before. Also remember: for `duplicated`, a missing value **equals** a missing value.

Write `drop_exact_duplicates(df)`. Return a tuple `(clean, n_removed)`:

- `clean` keeps the **first** copy of each row, in the original order, **with the original index labels** (do not
  reset the index: the labels tell you which rows survived).
- `n_removed` is the number of rows removed, as a plain `int`.
- Rows that differ in any column, even only by upper or lower case, are not duplicates.
- Two rows with missing values in the same places and equal values elsewhere **are** duplicates.
- Do not change `df`.

## Example

```python
import pandas as pd

df = pd.DataFrame({
    "id": [1, 2, 2, 3, 3, 4, 4],
    "city": ["Pune", "Delhi", "Delhi", "Pune", "pune", None, None],
    "age": [25, 30, 30, 41, 41, None, None],
})
clean, n = drop_exact_duplicates(df)
print(clean.index.tolist(), n, len(df))
```

```text
[0, 1, 3, 4, 5] 2 7
```

Rows 2 and 6 are removed. Row 4 stays: `pune` is not `Pune`.
