## Hint 1

You cannot write `WHERE price > AVG(price)` (aggregates are not allowed in `WHERE`). How can you get the average as
a single value first, and then compare each row to it?

## Hint 2

```
SELECT title, price
FROM books
WHERE price > ( SELECT AVG(?) FROM books )
ORDER BY price DESC, title;
```
