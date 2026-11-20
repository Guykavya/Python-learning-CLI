# Soft delete with a unique email

Many systems never delete a customer row: they set `deleted_at` (a **soft delete**), so orders and history stay intact. The problem: `email TEXT UNIQUE` then blocks a person who left from signing up again with the same address.

Write the string `SCHEMA` (SQL, several statements) that creates:

- a table `customers(id INTEGER PRIMARY KEY, email TEXT NOT NULL, name TEXT NOT NULL, deleted_at TEXT)`; `deleted_at` is `NULL` for live customers;
- a **partial unique index** so that among **live** customers (`deleted_at IS NULL`) an e-mail address can appear only once, while deleted rows may repeat it (chapter section 4.6);
- a view `active_customers(id, email, name)` that lists only the live customers.

The e-mail column itself must **not** carry a plain `UNIQUE` constraint.

## Example

```sql
INSERT INTO customers(email, name) VALUES ('a@x.com', 'Asha');
UPDATE customers SET deleted_at = '2026-01-01' WHERE id = 1;           -- soft delete
INSERT INTO customers(email, name) VALUES ('a@x.com', 'Asha again');   -- allowed
INSERT INTO customers(email, name) VALUES ('a@x.com', 'Copy');         -- UNIQUE error
```
