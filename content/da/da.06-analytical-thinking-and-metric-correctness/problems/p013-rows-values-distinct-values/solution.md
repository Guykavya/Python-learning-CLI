## Approach

`len` counts every row. `Series.count()` counts the non-missing cells. `Series.nunique()` counts different non-missing values.
The three numbers differ whenever the table has missing values and repeated customers.

## Code

```python
def three_counts(payments):
    return {
        "rows": int(len(payments)),
        "with_method": int(payments["method"].count()),
        "distinct_customers": int(payments["customer_id"].nunique()),
    }
```

## Complexity

`len` is O(1); `count` and `nunique` are O(n).

## Another way

In SQL the same trio is `COUNT(*)`, `COUNT(method)` and `COUNT(DISTINCT customer_id)`; problem 32 builds that query.
In pandas `payments.agg(...)` or `payments.count()` (all columns at once) show the missing values per column in one call.
