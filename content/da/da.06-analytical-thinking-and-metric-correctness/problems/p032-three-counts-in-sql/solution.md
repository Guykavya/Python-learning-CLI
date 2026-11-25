## Approach

One aggregate query, no `GROUP BY`, three different counts:

- `COUNT(*)` counts rows (including rows full of NULLs).
- `COUNT(method)` counts rows where `method` is not NULL. An empty text `''` is a value, so it is counted.
- `COUNT(DISTINCT customer_id)` counts different non-NULL customers, so the NULL customer is not "a customer".

## Code

```python
QUERY = """
SELECT COUNT(*)                    AS rows,
       COUNT(method)               AS with_method,
       COUNT(DISTINCT customer_id) AS distinct_customers
FROM payments
"""
```

## Complexity

One pass over the table; `DISTINCT` needs a set of the seen customers (O(n) memory in the worst case).

## Another way

`SUM(CASE WHEN method IS NOT NULL THEN 1 ELSE 0 END)` is the long form of `COUNT(method)`. For the customers,
`SELECT COUNT(*) FROM (SELECT DISTINCT customer_id FROM payments WHERE customer_id IS NOT NULL)` gives the same number.
