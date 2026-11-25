# Per job or per customer?

Chapter section 6.2. "Average items" is not one number: the **unit** of the average (job, customer) belongs in the name.

`jobs` has `job_id, customer_id`. `items` has `job_id, line_no` (one row per line item; a job may have no lines, and a
line may point at a job that is not in `jobs`). Write two functions:

- `items_per_job(jobs, items)`: line items of the known jobs divided by the number of jobs. A job without lines is still a job.
- `items_per_customer(jobs, items)`: the same line items divided by the number of **different customers** who have a job.

Lines of unknown jobs belong to nobody and are not counted. When the denominator is 0, return `None`.
Plain `float`s; never change the inputs.

## Example

```python
import pandas as pd
from solution import items_per_customer, items_per_job

jobs = pd.DataFrame({"job_id": [1, 2, 3], "customer_id": [7, 7, 8]})
items = pd.DataFrame({"job_id": [1, 1, 2, 3], "line_no": [1, 2, 1, 1]})
print(items_per_job(jobs, items), items_per_customer(jobs, items))
```

prints

```text
1.3333333333333333 2.0
```

Four lines, three jobs: 1.33 per job. The same four lines, two customers: 2.0 per customer.
