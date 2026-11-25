## Approach

Two `isin` checks, one for each direction. A missing `customer_id` is never `in` the customer table, so it is picked up
without extra code.

## Code

```python
def orphans(jobs, customers):
    known = customers["customer_id"]
    jobs_without_customer = jobs.loc[~jobs["customer_id"].isin(known), "job_id"]
    customers_without_job = customers.loc[~known.isin(jobs["customer_id"]), "customer_id"]
    return {
        "jobs_without_customer": sorted(jobs_without_customer.tolist()),
        "customers_without_job": sorted(customers_without_job.tolist()),
    }
```

## Complexity

O(n + m) with hash lookups.

## Another way

A left `merge(..., indicator=True)` of jobs onto customers (the customers' key made unique first) marks `left_only` rows,
which are the orphan jobs. `isin` is shorter and cannot multiply rows.
