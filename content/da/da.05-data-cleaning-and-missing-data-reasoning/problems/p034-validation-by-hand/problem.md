# Validation by hand

Chapter section 10.1. Cleaning is a claim; validation tests the claim. A hand-built validator takes a set of **named
rules** and reports, for each rule that fails, how many rows broke it and where the first ones are.

Write `validate_table(df, rules)`:

- `rules` is a dict `{rule name: function}`. Each function takes the **whole table** and returns a Boolean Series with
  the index of `df`: `True` where the row is **fine**, `False` where it breaks the rule. A missing value (`NaN`/`NA`)
  in the returned Series counts as fine.
- Return a **list** with one tuple `(rule, n_failed, first_ids)` for every rule that has at least one failing row,
  in the order of the rules. `n_failed` is an `int`; `first_ids` is a list of the **index labels** of the first (up to)
  three failing rows, in table order.
- A table that passes every rule gives `[]`. Do not change `df`.

## Example

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"id": [1, 2, 2, 4, 5],
                   "age": [25, 17, 130, np.nan, 40],
                   "city": ["Pune", "Delhi", "Goa", "Pune", "Pune"]},
                  index=[100, 101, 102, 103, 104])
rules = {
    "id is unique": lambda d: ~d["id"].duplicated(keep=False),
    "age in 18..75": lambda d: d["age"].between(18, 75) | d["age"].isna(),
    "city is known": lambda d: d["city"].isin(["Pune", "Delhi"]),
}
print(validate_table(df, rules))
```

```text
[('id is unique', 2, [101, 102]), ('age in 18..75', 2, [101, 102]), ('city is known', 1, [102])]
```

The rules decide what a missing value means: here the age rule says `| d["age"].isna()`, so the missing age is fine
(presence is a different question from range).
