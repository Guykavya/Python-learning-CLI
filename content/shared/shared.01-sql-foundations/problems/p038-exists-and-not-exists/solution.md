## Approach

Each subquery is **correlated**: it refers to the outer row (`c.customer_id`, `b.book_id`). `EXISTS` keeps the outer row if the subquery finds something; `NOT EXISTS` keeps it if the subquery finds nothing. No duplicates can occur, because each outer row is kept or dropped once.

## Code

```sql
-- QUERY_A
SELECT c.name
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o
              WHERE o.customer_id = c.customer_id AND o.status = 'shipped')
ORDER BY c.name;

-- QUERY_B
SELECT b.title
FROM books b
WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.book_id = b.book_id)
ORDER BY b.title;
```

## Complexity

Conceptually one subquery run per outer row, but with an index on `orders.customer_id` and `order_items.book_id` each probe is a quick lookup and stops at the first match (EXISTS short-circuits). Roughly O(n log m).

## Another way / portable SQL

`QUERY_A` with `IN`, or with `JOIN ... DISTINCT`. `QUERY_B` as an anti-join: `LEFT JOIN order_items oi ON ... WHERE oi.book_id IS NULL`. Prefer `NOT EXISTS` over `NOT IN`: it is not broken by NULLs (next trace problem shows why).
