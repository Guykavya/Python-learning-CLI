# INNER JOIN: books with their authors

`books.author_id` points to `authors.author_id`. A **join** lines up rows of two tables using a condition after `ON`.
An `INNER JOIN` keeps only pairs that match: a book without a matching author, or an author without books, disappears.

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

Return two columns, `title` and `author` (the author's name, aliased), one row per book that has an author.
Row order does not matter. Use a join. Put the SQL in `QUERY`.

**Example (a different pair).** `SELECT b.title, a.country FROM books b JOIN authors a ON a.author_id = b.author_id` gives each title with its author's country.
