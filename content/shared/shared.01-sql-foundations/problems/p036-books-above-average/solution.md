## Approach

The inner `SELECT AVG(price) FROM books` returns one row and one column, so it behaves like a number. The outer query compares every book's price to it. Because the inner query does not mention the outer row, it is computed once.

## Code

```sql
SELECT title, price
FROM books
WHERE price > (SELECT AVG(price) FROM books)
ORDER BY price DESC, title;
```

## Complexity

Two scans of `books`: one for the average, one for the filter. O(n). The engine evaluates an uncorrelated scalar subquery once and reuses the value.

## Another way / portable SQL

Cross join the average: `FROM books b CROSS JOIN (SELECT AVG(price) AS avg_price FROM books) a WHERE b.price > a.avg_price`. That version also lets you show `avg_price` as a column. Both are portable.
