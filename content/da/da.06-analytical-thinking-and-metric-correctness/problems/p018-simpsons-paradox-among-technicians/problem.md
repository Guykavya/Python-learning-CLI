# Simpson's paradox among technicians

Chapter section 6.4. A trend that holds inside every group can reverse when the groups are combined, because the groups
have different mixes. Here the groups are kinds of job, and the "trend" is which technician completes more jobs.

`jobs` has `job_id, tech, job_type, status`. The **rate** of a group is the share of its jobs with status `completed`.

Write two functions:

1. `completion_by_tech(jobs)` returning `{"overall": {tech: rate}, "by_type": {job_type: {tech: rate}}}`. A technician appears
   under a job type only if they worked on it. Rates are plain `float`s.
2. `paradox(jobs, a, b)` returning `True` when technician `a` has a **higher** rate than `b` in **every** job type that both
   worked on, and yet a **lower** overall rate. Job types worked on by only one of them are skipped in the first part (but
   they are part of the overall rate). With no job type in common, return `False`. Return a plain `bool`.

Never change `jobs`.

## Example

```python
import pandas as pd
from solution import completion_by_tech, paradox

rows = ([("A", "easy", "completed")] + [("A", "hard", "completed")] + [("A", "hard", "failed")] * 3
        + [("B", "easy", "completed")] * 3 + [("B", "easy", "failed")] + [("B", "hard", "failed")])
jobs = pd.DataFrame(rows, columns=["tech", "job_type", "status"])
jobs.insert(0, "job_id", range(1, len(jobs) + 1))
print(completion_by_tech(jobs))
print(paradox(jobs, "A", "B"), paradox(jobs, "B", "A"))
```

prints

```text
{'overall': {'A': 0.4, 'B': 0.6}, 'by_type': {'easy': {'A': 1.0, 'B': 0.75}, 'hard': {'A': 0.25, 'B': 0.0}}}
True False
```

A is better in easy jobs (1.0 against 0.75) and in hard jobs (0.25 against 0.0), yet B is better overall (0.6 against 0.4):
A was given four hard jobs out of five, B four easy ones. The overall rate is a weighted average of the two rates with
different weights for each technician.
