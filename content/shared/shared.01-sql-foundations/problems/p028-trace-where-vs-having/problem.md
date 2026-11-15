# Trace: WHERE before, HAVING after

A query is *evaluated* in this order, not in the order you write it:
`FROM` -> `WHERE` -> `GROUP BY` -> `HAVING` -> `SELECT` -> `ORDER BY`.
So `WHERE` removes rows **before** the groups are made, and `HAVING` removes whole groups **after** the aggregates exist.

Run this in your head (do not run it yet):

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'A','fiction',12.0),(2,'B','fiction',8.0),(3,'C','fiction',15.0),(4,'D','tech',30.0),(5,'E','tech',9.0),(6,'F','food',11.0),(7,'G','food',14.0);

SELECT category, COUNT(*) AS n, MAX(price) AS top
FROM books
WHERE price > 10
GROUP BY category
HAVING COUNT(*) >= 2
ORDER BY category;
```

Write the result in `answer.txt`:

- one line per result row, in the order the query returns them;
- values joined with `|` and no spaces, e.g. `Ada|3|NULL`;
- `NULL` for a NULL, strings without quotes, no header line;
- a `REAL` number prints the way Python prints a float (`15.0`, `7.5`);
- if the query returns no rows, write the single line `(no rows)`.

**Example (a different query).** `SELECT category, COUNT(*) FROM books GROUP BY category ORDER BY category;` over the
rows `(1,'x','a')`, `(2,'y','a')`, `(3,'z','b')` gives

```
a|2
b|1
```
