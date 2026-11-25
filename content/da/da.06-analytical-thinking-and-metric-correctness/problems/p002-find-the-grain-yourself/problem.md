# Find the grain yourself

Chapter section 3.3. You receive a table with no documentation. What is one row? Propose keys and test them. This
problem automates the search.

Write `candidate_keys(df, max_cols=2)`. It returns every **minimal** set of columns that identifies a row:

- the columns together have **no repeated combination** of values, and **no missing value** in any of them;
- **minimal**: if a smaller set already is a key, do not list any set that contains it (`("payment_id", "kind")` is
  useless when `payment_id` alone is unique);
- only sets of 1 to `max_cols` columns are tried;
- return a list of tuples of column names, shortest sets first, and inside one size in the order the columns appear in the table
  (tuples keep the table's column order). Return `[]` when nothing is unique.
- Never change the table.

## Example

```python
import pandas as pd
from solution import candidate_keys

pay = pd.DataFrame({"payment_id": [9, 8, 7, 6], "job_id": [1, 1, 2, 2],
                    "kind": ["deposit", "balance", "deposit", "balance"]})
print(candidate_keys(pay))
```

prints

```text
[('payment_id',), ('job_id', 'kind')]
```

`payment_id` alone is unique. `job_id` and `kind` are not unique alone, but the pair is: one deposit and one balance
per job. A key is a claim about the business, so a pair like this is a good question for the data owner.
