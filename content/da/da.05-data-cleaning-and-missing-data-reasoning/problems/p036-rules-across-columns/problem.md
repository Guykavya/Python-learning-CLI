# Rules across columns

Chapter section 11.4. Some errors are invisible column by column: every date is valid, every age is in range, but
the **relation** is wrong. Pandera checks relations with **dataframe-level checks**, passed to `checks=` of the schema.
A check receives the whole DataFrame and returns a Boolean Series (`True` = fine).

In `solution.py` define a module-level `SCHEMA` (a `pa.DataFrameSchema`) for a table of app users:

| column | type | rule |
|---|---|---|
| `user_id` | `int` | unique |
| `signup` | datetime (coerce it) | none on its own |
| `last_seen` | datetime (coerce it) | none on its own |
| `age` | `int` | from 13 to 100 |
| `student` | `bool` | none on its own |

and **two** dataframe-level checks:

1. `last_seen` is **not before** `signup` (the same day is fine);
2. **if** the user is a student **then** the age is below 30 (a student of 35 is a violation; a non-student of any
   age is fine).

The tests validate tables with `lazy=True` and read the **row indexes** of the failures from
`SchemaErrors.failure_cases["index"]` (they never read the error text). Each frame has a non-default index, so you
see labels, not positions.

## Example

```python
import pandas as pd
import pandera.pandas as pa

users = pd.DataFrame({
    "user_id": [1, 2, 3],
    "signup": pd.to_datetime(["2025-01-01", "2025-03-10", "2025-05-01"]),
    "last_seen": pd.to_datetime(["2025-02-01", "2025-03-02", "2025-05-01"]),
    "age": [20, 40, 35],
    "student": [True, False, True],
}, index=[10, 11, 12])
try:
    SCHEMA.validate(users, lazy=True)
except pa.errors.SchemaErrors as e:
    print(sorted(set(e.failure_cases["index"])))
```

```text
[11, 12]
```

Row 11 was last seen before it signed up; row 12 is a student aged 35. Row 10 breaks nothing.
