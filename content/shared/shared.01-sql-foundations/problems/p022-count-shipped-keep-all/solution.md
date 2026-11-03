## Approach

Put the status test in `ON`, so customers without shipped orders keep one row of NULLs. `COUNT(o.order_id)` ignores those NULLs and gives 0 for them. Group by the customer key.

## Code

```python
QUERY = """
SELECT c.name, COUNT(o.order_id) AS shipped_orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status = 'shipped'
GROUP BY c.customer_id, c.name
"""
```

## Complexity

One lookup per customer, then a grouping pass (hash or sort), roughly O(n log n).

## Another way / portable SQL

Conditional aggregation: `LEFT JOIN orders o ON ... ` with `SUM(CASE WHEN o.status = 'shipped' THEN 1 ELSE 0 END)` counts the same without the status in `ON`. A correlated subquery `(SELECT COUNT(*) FROM orders ...)` is a third way. In PostgreSQL/MySQL, selecting `c.name` while grouping by `c.customer_id` also works if `customer_id` is the primary key.
