# Check the grain

Chapter section 2.4. A claim like "one row per job" is only a claim until a test confirms it. The chapter's
`check_grain` printed a report. A function you can call in a pipeline must **stop** the pipeline, so yours raises.

Write `check_grain(df, key, name="")` in `solution.py`.

- `key` is one column name (`"job_id"`) or a list of column names (`["job_id", "line_no"]`).
- If the key is unique and no key cell is missing, return `True`.
- If any key cell is missing, raise `ValueError` whose message contains the word `missing`.
- If some key values repeat, raise `ValueError` with exactly this message shape:

  `<name>: key <key as a list> is not unique: <N> duplicate rows, e.g. <examples>`

  `N` is the number of **extra** rows (rows beyond the first of each key value). `examples` is a list of at most 5
  repeated key values, in order of first appearance. With a composite key each example is a tuple.
- Never change the table.

## Example

```python
import pandas as pd
from solution import check_grain

items = pd.DataFrame({"job_id": [5001, 5001, 5002], "line_no": [1, 2, 1]})
print(check_grain(items, ["job_id", "line_no"], "items"))
try:
    check_grain(items, "job_id", "items")
except ValueError as e:
    print(e)
```

prints

```text
True
items: key ['job_id'] is not unique: 1 duplicate rows, e.g. [5001]
```

Job 5001 appears twice, so there is **1** extra row. Each column of `items` alone is not a key, the pair is.
