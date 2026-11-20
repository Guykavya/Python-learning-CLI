# Sort for free with a covering index

"Show the latest 20 orders of a customer" is the most common list in a shop. The table:

```sql
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status      TEXT NOT NULL,
    created     TEXT NOT NULL,
    total_paise INTEGER NOT NULL
);
```

Write two strings in `solution.py`:

- `INDEX`: one `CREATE INDEX` statement on `orders`;
- `QUERY`: a `SELECT` with exactly one `?` (the customer id) that returns `id, created` of the customer's **20 latest orders**, ordered by `created` descending and then `id` descending.

The plan of your query must show:

- a **`COVERING INDEX`** (the query is answered from the index alone, without reading the table);
- **no `USE TEMP B-TREE`** (the sort is free: the index is already in the right order).

The rows must equal those of the naive query (`ORDER BY created DESC, id DESC LIMIT 20`) for every customer in the test data, including customers with fewer than 20 orders and several orders created at the same moment.
