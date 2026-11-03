# SUM, AVG, MIN, MAX with NULLs

Aggregate functions **ignore NULL values**. That is usually what you want, but it changes what
`AVG` means: it divides by the number of *non-NULL* values, not by the number of rows.

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, pages INTEGER);
INSERT INTO books VALUES (1,'T1',100),(2,'T2',200),(3,'T3',NULL),(4,'T4',300);
```

`pages` is NULL when the page count is not known. Return **one row** with these columns, in this order:

| column | meaning |
|---|---|
| `total_pages` | sum of the known page counts |
| `avg_known` | average of the known page counts |
| `shortest` | smallest known page count |
| `longest` | largest known page count |
| `avg_if_zero` | average when an unknown count is treated as 0 (use `COALESCE`) |

**Example.** For pages `100, 200, NULL, 300` the row is `(600, 200.0, 100, 300, 150.0)`:
`avg_known = 600 / 3`, but `avg_if_zero = 600 / 4`.

Note what happens when *every* page count is NULL. Your query must then give `NULL` for the first four
columns (that is what SQL does), and `0.0` for `avg_if_zero`.
