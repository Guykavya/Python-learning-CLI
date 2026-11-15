## Approach

Group by author, keep the groups whose count is at least 2, and order. `HAVING` runs after `GROUP BY`, so it can see the count.

## Code

```sql
SELECT author_id, COUNT(*) AS n_books
FROM books
GROUP BY author_id
HAVING COUNT(*) >= 2
ORDER BY n_books DESC, author_id;
```

## Complexity

Same as a plain `GROUP BY`: one pass plus per-group state. `HAVING` costs almost nothing extra: it only tests each finished group.

## Another way / portable SQL

A subquery does the same: `SELECT * FROM (SELECT author_id, COUNT(*) AS n_books FROM books GROUP BY author_id) WHERE n_books >= 2`. In MySQL and SQLite you may use the alias in `HAVING` (`HAVING n_books >= 2`); PostgreSQL does not allow that, so repeat the expression.
