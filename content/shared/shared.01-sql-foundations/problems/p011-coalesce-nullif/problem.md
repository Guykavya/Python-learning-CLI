# COALESCE and NULLIF

- `COALESCE(a, b, ...)` returns the **first value that is not NULL**. It is the standard way to supply a default.
- `NULLIF(a, b)` returns NULL when `a = b`, otherwise `a`. It turns a "fake" value (such as `''`) into a real NULL.

The signup form sometimes stored an empty string `''` instead of NULL for an unknown city.

```sql
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,            -- NULL when unknown
  joined      TEXT NOT NULL    -- 'YYYY-MM-DD'
);
INSERT INTO customers VALUES
 (1, 'Asha', 'Pune', '2023-01-10'),
 (2, 'Ben',  NULL,   '2023-02-03'),
 (3, 'Chen', '',     '2023-02-20'),
 (4, 'Dia',  NULL,   '2023-04-01'),
 (5, 'Eli',  'Pune', '2023-05-12');
```

Write three queries. Each returns two columns, `name` and `city` (the column must be called `city`).
Row order does not matter.

- `QUERY_A`: show `'unknown'` instead of NULL. (Empty strings stay as they are.)
- `QUERY_B`: show NULL instead of an empty string. (Real NULLs stay NULL.)
- `QUERY_C`: both: NULL **and** empty city show as `'unknown'`.

**Example (a different question).** `COALESCE(pages, 0) AS pages` shows 0 for unknown pages.
