# Aggregate before you join

Chapter section 4.3, habit 1: state the grain you want, then reach it. You want one row **per customer** with the money
quoted and the money paid.

`jobs` has `job_id, customer_id, quote_total` (one row per job). `payments` has `payment_id, job_id, amount` (a job can
have a deposit and a balance, so several rows). A payment may point at a job that does not exist.

Write `paid_per_customer(jobs, payments)` returning a table **indexed by `customer_id`**, one row per customer who has a
job, with two integer columns:

- `quoted`: the sum of `quote_total` of the customer's jobs (each job once);
- `paid`: the sum of the payments of the customer's jobs (`0` when none).

Payments of unknown jobs belong to nobody and are ignored. Use `validate="1:1"` on the join, so that pandas itself would
protest if the payments were not summed per job first. Never change the inputs.

## Example

```python
import pandas as pd
from solution import paid_per_customer

jobs = pd.DataFrame({"job_id": [1, 2], "customer_id": [7, 7], "quote_total": [1000, 500]})
payments = pd.DataFrame({"payment_id": [1, 2, 3], "job_id": [1, 1, 2], "amount": [300, 700, 500]})
print(paid_per_customer(jobs, payments).to_dict("index"))
print(int(jobs.merge(payments, on="job_id")["quote_total"].sum()))
```

prints

```text
{7: {'quoted': 1500, 'paid': 1500}}
2500
```

The plain join gives a quote total of 2500 (job 1's 1000 appears twice because it has two payments); summing the
payments per job first keeps it at 1500.
