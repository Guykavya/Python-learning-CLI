# Two columns and one alias

The shop wants a simple price list. A `SELECT` picks **columns** (the projection) from a table, and
`AS` gives a column a new name in the result. The `FROM` clause says which table to read.

The table (also used by the tests, with different rows):

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
 (7, 'Night Train',     4, 'mystery',  9.99, '2022-09-09', 310),
 (8, 'Paper Moons',     4, 'fiction', 14.25, '2017-06-25', NULL);
```

Write one `SELECT` that returns **two columns**, in this order:

1. `title`
2. the book's `price`, but named `cost` in the result (use an alias)

Return every book. The order of the rows does not matter. In `solution.py`, put the SQL in `QUERY`.

**Example (a different question).** `SELECT title AS name FROM books` returns one column called
`name` that holds the 8 titles.
