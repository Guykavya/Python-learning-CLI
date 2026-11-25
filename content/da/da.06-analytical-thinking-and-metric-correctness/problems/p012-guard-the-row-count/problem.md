# Guard the row count

Chapter section 13 (the toolkit) and habit 2 of section 4.3: compare the counts before and after a join. A check that
only prints is easy to miss; a check that raises stops the analysis.

Write `assert_rows_unchanged(before, after, label)`:

- if `after` has the same number of rows as `before`, return `after` (so the call can sit inside a pipeline);
- if it has **more** rows, raise `AssertionError` with the message `fan-out in <label>: <before> → <after> rows`;
- if it has **fewer** rows, raise `AssertionError` with the message `rows lost in <label>: <before> → <after> rows`.

The arrow is the single character `→` (U+2192). Never change the frames.

## Example

```python
import pandas as pd
from solution import assert_rows_unchanged

jobs = pd.DataFrame({"job_id": [1, 2, 3]})
payments = pd.DataFrame({"job_id": [1, 1, 2], "amount": [300, 700, 400]})
joined = jobs.merge(payments, on="job_id", how="left")
try:
    assert_rows_unchanged(jobs, joined, "jobs + payments")
except AssertionError as e:
    print(e)
print(len(assert_rows_unchanged(jobs, jobs, "same")))
```

prints

```text
fan-out in jobs + payments: 3 → 4 rows
3
```

Job 1 has two payments, so the left join grew from 3 to 4 rows.
