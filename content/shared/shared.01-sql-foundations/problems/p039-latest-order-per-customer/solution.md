## Approach

For every customer row, the inner query sorts that customer's orders newest first (date descending, id descending as tie-break) and takes the first. The outer `WHERE` keeps only the order whose id equals that answer.

## Code

```sql
SELECT c.name, o.order_id, o.ordered
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id = (
    SELECT o2.order_id
    FROM orders o2
    WHERE o2.customer_id = c.customer_id
    ORDER BY o2.ordered DESC, o2.order_id DESC
    LIMIT 1
)
ORDER BY c.name;
```

## Complexity

One subquery run per candidate row. With an index on `orders(customer_id, ordered)` each run is a short index lookup. Without one it scans the customer's orders: O(orders per customer) each, O(n^2) worst case for one huge customer.

## Another way / portable SQL

`o.ordered = (SELECT MAX(ordered) ...)` is the common form but returns both rows on a date tie. Window functions (`ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered DESC, order_id DESC)`) solve it in one pass; they come later in the chapter. `LIMIT` inside a subquery works in SQLite, MySQL (not in `IN` subqueries) and PostgreSQL.
