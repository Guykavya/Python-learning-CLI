# What relationship do two tables have?

Chapter section 3.4. Before a join, say which relationship you expect and test both sides. The chapter's
`relationship` returned only a word. Yours also counts the orphans, because an orphan is usually the real finding.

Write `relationship(left, right, left_key, right_key)` returning a dict with three entries:

- `"relationship"`: `"1:1"`, `"1:m"`, `"m:1"` or `"m:m"`. A side is "1" when its key column is unique (`is_unique`),
  otherwise "m".
- `"left_orphans"`: the number of **rows** of `left` whose key does not appear in `right`'s key column.
- `"right_orphans"`: the number of **rows** of `right` whose key does not appear in `left`'s key column.

A missing key (NaN) matches nothing, so such a row is an orphan. Never change the tables.

## Example

```python
import pandas as pd
from solution import relationship

customers = pd.DataFrame({"customer_id": [1, 2, 3]})
jobs = pd.DataFrame({"job_id": [10, 11, 12], "customer_id": [1, 1, 9]})
print(relationship(customers, jobs, "customer_id", "customer_id"))
print(relationship(jobs, customers, "customer_id", "customer_id"))
```

prints

```text
{'relationship': '1:m', 'left_orphans': 2, 'right_orphans': 1}
{'relationship': 'm:1', 'left_orphans': 1, 'right_orphans': 2}
```

Customers 2 and 3 have no job (2 left orphans); job 12 points at customer 9 who does not exist (1 right orphan).
Swapping the tables swaps both the relationship and the orphan counts.
