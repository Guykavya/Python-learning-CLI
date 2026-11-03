# LIKE, IN and BETWEEN

Three short tests that make `WHERE` easier to read:

- `title LIKE 'S%'`: `%` matches any run of characters, `_` matches exactly one character.
- `category IN ('tech', 'cooking')`: equal to any value in the list.
- `price BETWEEN 10 AND 18`: **inclusive** at both ends (same as `price >= 10 AND price <= 18`).

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

Write three queries, each returning one column `title` (row order does not matter):

- `QUERY_A`: titles that **start with** the letter S.
- `QUERY_B`: titles of books in the category `tech` or `cooking`. Use `IN`.
- `QUERY_C`: titles of books whose price is from 10 to 18, both ends included. Use `BETWEEN`.

**Example (a different question).** Titles that end in `s`: `WHERE title LIKE '%s'`.
