## Approach

Group by `category`. In each group `COUNT(*)` is the number of rows and `AVG(price)` the mean. Round last, and sort the final rows.

## Code

```sql
SELECT category,
       COUNT(*)              AS n_books,
       ROUND(AVG(price), 2)  AS avg_price
FROM books
GROUP BY category
ORDER BY category;
```

## Complexity

One pass, then the engine keeps one running state per group (a hash table or a sort by `category`): O(n) or O(n log n). An index on `category` lets it read the rows already grouped.

## Another way / portable SQL

`GROUP BY 1` (position) works in SQLite, MySQL and PostgreSQL, but a name is clearer. PostgreSQL's `ROUND(double, 2)` needs a `numeric` (`ROUND(AVG(price)::numeric, 2)`).
