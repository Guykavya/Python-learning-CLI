# Predict the explosion

Chapter section 4.4. In a many-to-many join every pair of matching rows becomes a row: a job with 2 payments and
3 lines gives 6 rows. You can **predict** the size of a join from the key counts before you spend memory on it, which
matters when the tables have millions of rows.

Write `rows_after_join(a, b, key)` that returns the number of rows of the **inner** join `a.merge(b, on=key)` without
calling `merge`:

- `key` is a column name or a list of column names;
- for every key value, the join has `count in a` times `count in b` rows;
- pandas joins **missing** key values with each other, so a missing key counts as one more key value;
- never change the tables.

## Example

```python
import pandas as pd
from solution import rows_after_join

payments = pd.DataFrame({"job_id": [1, 1, 2]})
items = pd.DataFrame({"job_id": [1, 1, 1, 2, 3]})
print(rows_after_join(payments, items, "job_id"))
print(len(payments.merge(items, on="job_id")))
```

prints

```text
7
7
```

Job 1: 2 payments x 3 lines = 6 rows; job 2: 1 x 1 = 1; job 3 has no payment, so no rows. Total 7.
