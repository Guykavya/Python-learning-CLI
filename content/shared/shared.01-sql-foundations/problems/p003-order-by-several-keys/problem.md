# ORDER BY several keys

`ORDER BY a, b DESC` sorts by `a` first. Only rows with the same `a` are sorted by `b`. Each key has its
own direction: `ASC` (the default) or `DESC`. Without `ORDER BY`, SQL promises **no** order at all.

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

Return `category`, `title`, `price` (in this order) for every book, sorted by:

1. `category`, A to Z
2. `price`, highest first (inside a category)
3. `title`, A to Z (to break ties)

The order of the rows **is** checked. Put the SQL in `QUERY`.

**Example.** For dataset A, the two `cooking` books both cost 18.00, so the title decides:
`Cooking Light` comes before `Salt and Stone`.
