# Trace: AND before OR

Precedence from strongest to weakest: comparison operators, then `NOT`, then `AND`, then `OR`.
So `a OR b AND c` is `a OR (b AND c)`, and `NOT a AND b` is `(NOT a) AND b`.

Table:

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
 (6, 'Night Train',     4, 'mystery',  9.99, '2022-09-09', 310);
```

Predict the result of each of the four queries (all end with `ORDER BY book_id`, so the order is fixed):

1. `SELECT title FROM books WHERE category = 'fiction' OR category = 'tech' AND price < 40 ORDER BY book_id;`
2. `SELECT title FROM books WHERE (category = 'fiction' OR category = 'tech') AND price < 40 ORDER BY book_id;`
3. `SELECT title FROM books WHERE NOT category = 'fiction' AND price < 15 ORDER BY book_id;`
4. `SELECT title FROM books WHERE NOT (category = 'fiction' AND price < 15) ORDER BY book_id;`


**How to write the answer.** Put one line per result row in `answer.txt`. Join the column
values of a row with `|` and no spaces. Write `NULL` for a NULL value. Write no header line and
no quotes around text. If a query returns no rows, write the single line `(no rows)`.
Put a line containing only `---` between the results of two queries (3 separator lines).

Example: a row with the values `Ada`, `3` and NULL is written as `Ada|3|NULL`.

**Example (a different table).** For `t(x)` holding 1, 2, 3, the query `SELECT x FROM t WHERE x = 1 OR x = 2 AND x > 5 ORDER BY x` gives only `1`.
