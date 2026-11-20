## Approach

```python
SCHEMA = """
CREATE TABLE customers (
    id         INTEGER PRIMARY KEY,
    email      TEXT NOT NULL,
    name       TEXT NOT NULL,
    deleted_at TEXT
);
CREATE UNIQUE INDEX customers_live_email ON customers(email) WHERE deleted_at IS NULL;
CREATE VIEW active_customers AS
    SELECT id, email, name FROM customers WHERE deleted_at IS NULL;
"""
```

A **partial index** contains only the rows that satisfy its `WHERE`. For a `UNIQUE` partial index the uniqueness applies to those rows only: two live customers cannot share an e-mail, but any number of deleted rows can. Without the `WHERE` part, the second sign-up of `a@x.com` would fail forever. The view hides the `deleted_at` bookkeeping from the code that lists customers.

Example: after the soft delete, row 1 has `deleted_at` set and is not in the index, so row 2 with the same e-mail is allowed; row 3 collides with row 2 and fails.

## Complexity

`O(log n)` per insert for the index.

## Another way

PostgreSQL has the same syntax. MySQL has no partial indexes; people use a generated column that is `NULL` for deleted rows and put a `UNIQUE` on it (`NULL`s never collide).

## Why it matters

Soft deletes keep history (orders still point at the customer) without trapping e-mail addresses, and the rule lives in the database, not in code that can forget it.
