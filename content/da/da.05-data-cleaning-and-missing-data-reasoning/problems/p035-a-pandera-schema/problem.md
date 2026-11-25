# A pandera schema

Chapter sections 11.1 to 11.3. A **schema** writes down the table you expect, so that every table can be checked
against it. Pandera (`import pandera.pandas as pa`) is installed in the course environment.

In `solution.py` define a module-level variable `SCHEMA`, a `pa.DataFrameSchema` for the survey table with these
columns (all columns must be present; other columns are allowed, so `strict=False`):

| column | type | rule | missing allowed? |
|---|---|---|---|
| `resp_id` | `int` | every value different from the others (`unique=True`) | no |
| `age` | `float` | from 18 to 75 (inclusive) | yes |
| `city` | `str` | one of `"Pune"`, `"Delhi"`, `"Mumbai"` | no |
| `income` | `float` | from 1,000 to 1,000,000 (inclusive) | yes |
| `satisfaction` | `int` | from 1 to 10 (inclusive) | no |
| `email` | `str` | contains an `@` | yes |

The tests validate one good table and seven bad tables with `SCHEMA.validate(df, lazy=True)`. Each bad table has one
mistake, and the failure must be reported on **exactly the column that has the mistake** (they read the column names
from `SchemaErrors.failure_cases`; they never read the error text). The good table contains missing ages, incomes and
emails: those must pass.

## Example

```python
import numpy as np
import pandas as pd
import pandera.pandas as pa

good = pd.DataFrame({
    "resp_id": [1, 2], "age": [25.0, np.nan], "city": ["Pune", "Delhi"],
    "income": [30000.0, np.nan], "satisfaction": [4, 9], "email": ["a@x.com", None],
})
print(SCHEMA.validate(good).shape)

bad = good.assign(age=[25.0, 150.0])
try:
    SCHEMA.validate(bad, lazy=True)
except pa.errors.SchemaErrors as e:
    print(sorted(set(e.failure_cases["column"])))
```

```text
(2, 6)
['age']
```
