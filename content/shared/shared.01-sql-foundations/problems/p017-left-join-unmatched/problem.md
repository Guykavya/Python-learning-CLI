# LEFT JOIN keeps unmatched rows

`A LEFT JOIN B ON ...` keeps **every row of A**. If a row of A has no match in B, it still appears once, with NULL in all of B's columns.

```sql
CREATE TABLE authors (
  author_id INTEGER PRIMARY KEY,
  name      TEXT NOT NULL,
  country   TEXT
);
INSERT INTO authors VALUES
 (1, 'Mira Das',  'India'),
 (2, 'Tom Hale',  'UK'),
 (3, 'Lena Voss', 'Germany'),
 (4, 'Omar Reed', 'UK'),
 (5, 'Zed Park',  'Japan');
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

Return every author with their books: columns `author` (the author's name) and `title`. An author with no books must appear
**once**, with `title` NULL. Row order does not matter. Put the SQL in `QUERY`.

**Example (a different pair).** `FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id` lists customers with no orders too, with NULL order columns.
