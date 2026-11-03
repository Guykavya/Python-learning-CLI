## Hint 1

If one of the four values is NULL, does `AVG(pages)` count it in the denominator? Which function can replace a NULL by a
number *before* the average is taken, so that the row does count?

## Hint 2

```
SELECT SUM(pages)              AS total_pages,
       AVG(pages)              AS avg_known,
       MIN(pages) ... MAX(pages) ...
       AVG( COALESCE(pages, ?) ) AS avg_if_zero
FROM books;
```
