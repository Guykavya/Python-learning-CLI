# Orphans

Chapter section 3.1. A foreign key that points nowhere is an **orphan**. In real data the orphans are often the finding:
test accounts, deleted customers, typing errors. Return the exact ids, not only a count.

Write `orphans(jobs, customers)`. The tables have `job_id` and `customer_id` in `jobs`, and `customer_id` in `customers`.
Return a dict with two entries:

- `"jobs_without_customer"`: the `job_id`s whose `customer_id` is not in `customers` (a **missing** `customer_id`
  counts), sorted;
- `"customers_without_job"`: the `customer_id`s of customers that appear in no job, sorted.

The lists contain plain Python `int`s. Never change the tables.

## Example

```python
import pandas as pd
from solution import orphans

customers = pd.DataFrame({"customer_id": [1, 2, 3]})
jobs = pd.DataFrame({"job_id": [12, 10, 11], "customer_id": [9, 1, 1]})
print(orphans(jobs, customers))
```

prints

```text
{'jobs_without_customer': [12], 'customers_without_job': [2, 3]}
```

Job 12 points at customer 9 who does not exist. Customers 2 and 3 have no job.
