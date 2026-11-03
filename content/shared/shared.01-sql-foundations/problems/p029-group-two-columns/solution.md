## Approach

Group by both columns, count, then sort by the count descending with two tie-breakers so the order is fully fixed.

## Code

```sql
SELECT customer_id, status, COUNT(*) AS n_orders
FROM orders
GROUP BY customer_id, status
ORDER BY n_orders DESC, customer_id DESC, status;
```

## Complexity

One pass; per-group state keyed by the pair (customer_id, status). O(n) with hashing or O(n log n) with sorting. A composite index on `(customer_id, status)` would let the engine read the groups in order.

## Another way / portable SQL

`GROUP BY 1, 2 ORDER BY 3 DESC, 1, 2` uses positions and works everywhere, but names are easier to read. MySQL and PostgreSQL behave the same.
