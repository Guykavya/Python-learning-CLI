# Trace: DISTINCT on one column, two columns, an expression

`DISTINCT` removes duplicate **result rows**. A row is a duplicate only if **all** selected columns (or
expressions) are equal to those of an earlier row. In SQLite a comparison such as `price >= 15` gives `1` (true) or `0` (false).

Predict the output of the four queries below, run in order against this table:

```sql
CREATE TABLE books (
  book_id   INTEGER PRIMARY KEY,
  title     TEXT NOT NULL,
  author_id INTEGER,
  category  TEXT NOT NULL,
  price     REAL NOT NULL,
  published TEXT NOT NULL,   -- 'YYYY-MM-DD'
  pages     INTEGER          -- NULL when unknown
);
INSERT INTO books VALUES
 (1, 'Quiet Rivers',    1, 'fiction', 12.50, '2019-03-10', 320),
 (2, 'Iron Garden',     1, 'fiction',  9.99, '2021-07-01', 280),
 (3, 'Data Basics',     2, 'tech',    39.00, '2020-01-15', 450),
 (4, 'SQL in Practice', 2, 'tech',    45.50, '2022-05-20', NULL),
 (5, 'Cooking Light',   3, 'cooking', 18.00, '2018-11-30', 200),
 (6, 'Salt and Stone',  3, 'cooking', 18.00, '2023-02-14', 240),
 (7, 'Night Train',     4, 'mystery',  9.99, '2022-09-09', 310);
```

Queries:

1. `SELECT DISTINCT category FROM books ORDER BY category;`
2. `SELECT DISTINCT category, author_id FROM books ORDER BY category, author_id;`
3. `SELECT DISTINCT price >= 15 AS pricey FROM books ORDER BY pricey;`
4. `SELECT DISTINCT price FROM books ORDER BY price DESC;`


**How to write the answer.** Put one line per result row in `answer.txt`. Join the column
values of a row with `|` and no spaces. Write `NULL` for a NULL value. Write no header line and
no quotes around text. If a query returns no rows, write the single line `(no rows)`.
Put a line containing only `---` between the results of two queries (3 separator lines in total).

Example: a row with the values `Ada`, `3` and NULL is written as `Ada|3|NULL`.

**Example (a different table).** For `t(x)` holding 1, 1, 2, the query `SELECT DISTINCT x FROM t ORDER BY x` gives:

```
1
2
```
