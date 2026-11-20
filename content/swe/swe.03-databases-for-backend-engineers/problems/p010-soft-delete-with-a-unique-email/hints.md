## Hint 1

A normal `UNIQUE` index looks at **all** rows. Which kind of index looks only at some rows? (Think of the `WHERE` clause on an index.)

## Hint 2

`CREATE UNIQUE INDEX name ON customers(email) WHERE deleted_at IS NULL;` The deleted rows are not in the index, so they cannot collide with anything.

## Hint 3

```text
CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT NOT NULL, name TEXT NOT NULL, deleted_at TEXT);
CREATE UNIQUE INDEX customers_live_email ON customers(email) WHERE deleted_at IS NULL;
CREATE VIEW active_customers AS SELECT id, email, name FROM customers WHERE deleted_at IS NULL;
```
