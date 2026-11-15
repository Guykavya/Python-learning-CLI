## Hint 1

Write the helper first and run it alone: which query gives one row per `book_id` with the total quantity? What do you put in `GROUP BY`?
Then how do you attach the title, and where does the "at least 2" condition go: inside the helper (`HAVING`) or in the main query?

## Hint 2

```
WITH book_sales AS (
    SELECT book_id, SUM(qty) AS units
    FROM order_items
    GROUP BY ?
)
SELECT b.title, s.units
FROM books b
JOIN book_sales s ON s.book_id = b.?
WHERE s.units >= ?
ORDER BY s.units DESC, b.title;
```
