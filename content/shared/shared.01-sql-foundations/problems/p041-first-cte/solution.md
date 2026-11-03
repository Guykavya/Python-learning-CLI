## Approach

The CTE summarises the lines per book. The main query is then an ordinary join and filter. Because the CTE is already grouped, the filter is a plain `WHERE` on `units`.

## Code

```sql
WITH book_sales AS (
    SELECT book_id, SUM(qty) AS units
    FROM order_items
    GROUP BY book_id
)
SELECT b.title, s.units
FROM books b
JOIN book_sales s ON s.book_id = b.book_id
WHERE s.units >= 2
ORDER BY s.units DESC, b.title;
```

## Complexity

The CTE is computed by one pass over `order_items`; then one join. Same cost as the nested-subquery version: a CTE is a readability tool. (In SQLite a CTE used once is usually inlined; in PostgreSQL 12+ too.)

## Another way / portable SQL

Put the subquery directly in `FROM (SELECT ...) s`. Or skip the CTE and use `GROUP BY` with `HAVING SUM(qty) >= 2` after joining books to lines. `WITH` works in SQLite, PostgreSQL and MySQL 8+ (not MySQL 5.7).
