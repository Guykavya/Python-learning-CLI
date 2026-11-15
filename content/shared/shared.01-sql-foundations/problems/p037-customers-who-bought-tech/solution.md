## Approach

The inner query returns the ids of customers with a tech line (the same id may appear many times; that does not matter for `IN`). The outer query keeps customers whose id is in that list.

## Code

```sql
SELECT name
FROM customers
WHERE customer_id IN (
    SELECT o.customer_id
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN books b        ON b.book_id   = oi.book_id
    WHERE b.category = 'tech'
)
ORDER BY name;
```

## Complexity

The engine may build a temporary set of ids from the subquery (one pass over the joined rows) and probe it for each customer: roughly O(customers + lines). Duplicate ids in the subquery are harmless.

## Another way / portable SQL

`SELECT DISTINCT c.name FROM customers c JOIN orders ... WHERE b.category = 'tech'` gives the same names but needs `DISTINCT` because the join repeats Asha. `EXISTS` is a third form (next problem) and is the safest when the subquery column may contain NULL (see `NOT IN`).
