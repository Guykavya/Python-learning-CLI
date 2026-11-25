## Approach

The city is a customer attribute, so join the customers (many jobs to one customer, `validate="m:1"` keeps the join honest)
and group. The overall figure is computed from the job table directly: total over count, once.

## Code

```python
def avg_job_value(jobs, customers):
    joined = jobs.merge(customers[["customer_id", "city"]], on="customer_id", how="left", validate="m:1")
    by_city = joined.groupby("city")["quote_total"].mean()
    return {
        "overall": float(jobs["quote_total"].sum() / len(jobs)),
        "by_city": {city: float(v) for city, v in by_city.items()},
    }
```

## Complexity

O(n + m) for the join and the grouping.

## Another way

Keep `sum` and `count` per city, then `overall = sum of sums / sum of counts`; this is how you combine groups when you
only have the group results. The weighted mean of the city means with the city job counts as weights gives the same number.
