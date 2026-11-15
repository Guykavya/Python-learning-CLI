## Approach

Group by customer. Compute each count with a condition inside the aggregate. The `CASE` version turns every row into 1 or 0 and sums; the `FILTER` version tells `COUNT` which rows to count.

## Code

```sql
-- QUERY_A
SELECT customer_id,
       COUNT(*) AS total,
       SUM(CASE WHEN status = 'shipped'   THEN 1 ELSE 0 END) AS shipped,
       SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM orders
GROUP BY customer_id
ORDER BY customer_id;

-- QUERY_B
SELECT customer_id,
       COUNT(*) AS total,
       COUNT(*) FILTER (WHERE status = 'shipped')   AS shipped,
       COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled
FROM orders
GROUP BY customer_id
ORDER BY customer_id;
```

## Complexity

One pass over `orders` computes all counts together. Three separate queries with `WHERE` would scan the table three times. That is the practical reason for conditional aggregation.

## Another way / portable SQL

`COUNT(CASE WHEN status = 'shipped' THEN 1 END)` works everywhere because `COUNT` skips the NULL that a missing `ELSE` produces. In SQLite and MySQL `SUM(status = 'shipped')` is a short form (a comparison is 0 or 1). PostgreSQL needs `CASE` or `FILTER`.
