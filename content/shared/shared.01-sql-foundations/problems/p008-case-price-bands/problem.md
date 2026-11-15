# CASE: price bands

`CASE WHEN condition THEN value ... ELSE value END` is SQL's if/else **inside** a query. The first
`WHEN` that is true wins. Without `ELSE`, no match gives NULL.

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

Return `title` and a column named `band`, for every book:

- `'budget'` when the price is **below 10**
- `'standard'` when it is **at least 10 and below 20**
- `'premium'` when it is **20 or more**

Row order does not matter. Put the SQL in `QUERY`.

**Example (a different rule).** `CASE WHEN pages IS NULL THEN 'unknown' ELSE 'known' END AS pages_info`.
