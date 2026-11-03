## Hint 1

What decides which rows end up in the same group? Which column must appear in `GROUP BY`, and which columns may appear in `SELECT` without an aggregate?

## Hint 2

```
SELECT category, COUNT(*) AS n_books, ROUND( AVG(?), 2 ) AS avg_price
FROM books
GROUP BY ?
ORDER BY ?;
```
