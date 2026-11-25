# Three answers from one bad join

Chapter section 4.2. Someone has already joined `jobs` to `items` and handed you the result. You may not redo the join.
From the fanned-out table, compute three numbers correctly.

The table `joined` is `jobs.merge(items, on="job_id", how="left")`: one row per line item, with the job's `job_id` and
`quote_total` repeated on every line. A job without line items has **one** row where `line_no` is missing.

Write `correct_totals(joined)` returning a dict:

- `"jobs"`: the number of jobs;
- `"job_value"`: the sum of `quote_total` over jobs (each job once);
- `"items"`: the number of line items (a job without lines contributes none).

All three are plain `int`s. Never change `joined`.

## Example

```python
import pandas as pd
from solution import correct_totals

jobs = pd.DataFrame({"job_id": [1, 2, 3], "quote_total": [900, 400, 100]})
items = pd.DataFrame({"job_id": [1, 1, 2], "line_no": [1, 2, 1]})
joined = jobs.merge(items, on="job_id", how="left")
print(len(joined), int(joined["quote_total"].sum()))
print(correct_totals(joined))
```

prints

```text
4 2300
{'jobs': 3, 'job_value': 1400, 'items': 3}
```

The join has 4 rows and a naive quote sum of 2300 (job 1 is counted twice). The truth: 3 jobs, 1400 of quotes,
3 line items. Job 3 has no line, so its row is not an item.
