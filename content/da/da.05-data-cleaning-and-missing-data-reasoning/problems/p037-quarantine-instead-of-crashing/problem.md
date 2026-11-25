# Quarantine instead of crashing

Chapter sections 10.2 and 12.2. A pipeline that crashes on the first bad row is annoying; one that silently deletes
bad rows breaks the rule "flag before you delete". The middle road is a **quarantine**: the good rows go on, the bad
rows go to a separate table **with the reason**.

Write `split_valid(df, schema)`; `schema` is a `pandera.pandas.DataFrameSchema`:

- Validate `df` with `lazy=True` so that every failure is collected.
- Return `(valid, quarantine)`:
  - `valid`: the rows with **no** failure, in the original order, with their original index and columns;
  - `quarantine`: the rows with **at least one** failure, in the original order, with their original index and all the
    original columns **plus** a text column `reasons`: the **names of the failing columns**, sorted, without
    repeats, joined with `", "` (for example `"age, id"`).
- `valid` and `quarantine` together contain every row exactly once. If nothing fails, `quarantine` is empty but still
  has the `reasons` column.
- Failures that are **not tied to a row** (a missing column, a wrong dtype for the whole column) cannot be
  quarantined: **re-raise** the pandera exception (`SchemaErrors`) instead.
- Do not change `df`.

Hint about the source: `SchemaErrors.failure_cases` is a DataFrame; its `index` column holds the row label of each
failure (empty when the failure is not about a row), and `column` the column name.

## Example

```python
import numpy as np
import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "id": pa.Column(int, unique=True),
    "age": pa.Column(float, pa.Check.in_range(18, 75), nullable=True),
    "city": pa.Column(str, pa.Check.isin(["Pune", "Delhi"])),
})
df = pd.DataFrame({"id": [1, 2, 2, 4], "age": [20.0, 80.0, 30.0, np.nan],
                   "city": ["Pune", "Goa", "Delhi", "Pune"]})
valid, quarantine = split_valid(df, schema)
print(valid.index.tolist(), quarantine.index.tolist())
print(quarantine["reasons"].tolist())
```

```text
[0, 3] [1, 2]
['age, city, id', 'id']
```
