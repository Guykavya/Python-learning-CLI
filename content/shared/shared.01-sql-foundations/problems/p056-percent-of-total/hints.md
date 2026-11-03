## Hint 1

Which window gives the total of the whole table on each row? And which one gives the total of the row's category? What is the difference between the two `OVER` clauses?

## Hint 2

```
SELECT title, category, price,
       ROUND(100.0 * price / SUM(price) OVER (PARTITION BY <category>), 1) AS pct_category,
       ROUND(100.0 * price / SUM(price) OVER (), 1)                       AS pct_all
FROM books
ORDER BY book_id
```
