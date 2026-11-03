# String and date functions

SQLite stores dates as text `'YYYY-MM-DD'`. Useful functions: `length(s)`, `substr(s, start, count)`
(start counts from 1), `strftime('%Y', date)` (year as **text**), `julianday(date)` (a number of days).

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

Write three queries (row order does not matter):

- `QUERY_A`: columns `title`, `year`, `short`, `len` where `year` is the publication year (text, e.g. `'2019'`),
  `short` is the first 3 letters of the title, `len` is the number of characters in the title.
- `QUERY_B`: one column `title`: books published in the year 2022.
- `QUERY_C`: columns `title`, `days_old`: the whole number of days from the publication date to `'2024-01-01'`
  (use `CAST(... AS INTEGER)`).

**Example (a different question).** The month of a date: `strftime('%m', published)` gives `'03'` for March.
