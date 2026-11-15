## Approach

Two CTEs: the first order date per customer (this also defines the base: only customers with orders appear), and the customers having an order 1 to 30 days after it (`DISTINCT` so a customer with several qualifying orders counts once). The final row divides the two counts; `NULLIF(count, 0)` turns a division by zero into NULL.

## Code

```python
QUERY = """
WITH first_order AS (
  SELECT customer_id, MIN(ordered) AS first_day
  FROM orders
  GROUP BY customer_id
),
repeaters AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  JOIN first_order f ON f.customer_id = o.customer_id
  WHERE julianday(o.ordered) - julianday(f.first_day) BETWEEN 1 AND 30
)
SELECT (SELECT COUNT(*) FROM first_order) AS customers,
       (SELECT COUNT(*) FROM repeaters)   AS repeaters,
       ROUND(100.0 * (SELECT COUNT(*) FROM repeaters)
             / NULLIF((SELECT COUNT(*) FROM first_order), 0), 1) AS pct_repeat
"""
```

## Complexity

One group-by over `orders` and one join of `orders` with its per-customer summary: O(n log n). With an index on `(customer_id, ordered)` both steps can use it.

## Another way / portable SQL

One pass with a window: `MIN(ordered) OVER (PARTITION BY customer_id)` gives the first day on every row, then `COUNT(DISTINCT CASE WHEN days BETWEEN 1 AND 30 THEN customer_id END)`. In PostgreSQL dates subtract directly (`o.ordered - f.first_day`); in MySQL use `DATEDIFF(o.ordered, f.first_day)`.
