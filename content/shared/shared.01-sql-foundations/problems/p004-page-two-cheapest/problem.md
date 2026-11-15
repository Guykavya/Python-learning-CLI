# Page 2 of the cheapest books

The website lists books cheapest first, **3 books per page**. `LIMIT n` keeps at most n rows and
`OFFSET k` skips the first k rows. Paging is only stable if the sort order is fully decided, so ties
need a tie-break.

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

Return the `title` of the books on **page 2**: sort by `price` (lowest first), then by `title` A to Z for
equal prices. Page 1 is rows 1-3, page 2 is rows 4-6. One column: `title`. The order is checked.

**Example.** On dataset A the sorted list starts `Iron Garden, Night Train, Quiet Rivers, Paper Moons, ...`.
Page 1 is the first three of those, so page 2 starts with `Paper Moons`.
