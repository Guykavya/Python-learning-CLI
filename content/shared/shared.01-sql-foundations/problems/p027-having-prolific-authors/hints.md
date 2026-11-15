## Hint 1

You need a number per author first (a count), and then only some authors. Does the condition "at least 2" exist before
the grouping happens, or only after?

## Hint 2

```
SELECT author_id, COUNT(*) AS n_books
FROM books
GROUP BY ?
HAVING COUNT(*) ? 2
ORDER BY n_books ?, author_id ?;
```
