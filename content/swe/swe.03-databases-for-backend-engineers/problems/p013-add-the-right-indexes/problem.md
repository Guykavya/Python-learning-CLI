# Add the right indexes

A table with 20,000 rows is slow for three queries:

```sql
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status      TEXT NOT NULL,
    created     TEXT NOT NULL,
    total_paise INTEGER NOT NULL
);

-- A
SELECT * FROM orders WHERE customer_id = ?;
-- B
SELECT * FROM orders WHERE status = ? AND created >= ?;
-- C
SELECT * FROM orders WHERE customer_id = ? AND status = ?;
```

Write `INDEXES`: a **list of `CREATE INDEX` statements** such that every one of the three queries is answered with a `SEARCH` (an index), not a `SCAN`.

Rules:

- At most **3** indexes. (One index per column is not a strategy: think which index can serve more than one query.)
- Every statement must start with `CREATE INDEX`.
- Do not change the table.

The tests apply your statements to a table with 20,000 rows and read the plan of each query.
