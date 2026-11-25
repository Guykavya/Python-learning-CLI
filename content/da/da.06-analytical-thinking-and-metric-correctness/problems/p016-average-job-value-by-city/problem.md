# Average job value by city

Chapter section 6.1. "Never average averages. Add the numerators, add the denominators, and divide once."

`jobs` has `job_id, customer_id, quote_total`. `customers` has `customer_id, city` (one row per customer; a customer has one
city). Write `avg_job_value(jobs, customers)` returning a dict:

- `"overall"`: the average quote **per job** over all jobs (total quoted divided by the number of jobs);
- `"by_city"`: a dict `{city: average quote per job of the jobs of customers in that city}`. A city without jobs does not appear.

Use plain `float`s. Never change the inputs.

## Example

```python
import pandas as pd
from solution import avg_job_value

customers = pd.DataFrame({"customer_id": [1, 2], "city": ["Pune", "Delhi"]})
jobs = pd.DataFrame({"job_id": [1, 2, 3], "customer_id": [1, 1, 2], "quote_total": [100, 300, 800]})
print(avg_job_value(jobs, customers))
```

prints

```text
{'overall': 400.0, 'by_city': {'Delhi': 800.0, 'Pune': 200.0}}
```

Pune has two jobs (mean 200), Delhi one (mean 800). The overall mean is 1200 / 3 = 400. The mean of the two city means
would be 500: Delhi's single job would count as much as Pune's two.
