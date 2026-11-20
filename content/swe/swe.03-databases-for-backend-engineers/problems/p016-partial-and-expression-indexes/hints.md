## Hint 1

For Q1, a plain index on `email` does not help: the query compares `lower(email)`, not `email`. What kind of index stores the result of a function?

## Hint 2

For Q2, only the open tickets matter. An index with a `WHERE` clause holds only those rows. Which column should it be sorted by, so that `ORDER BY created` is free?

## Hint 3

```text
CREATE INDEX idx_users_email_lower ON users(lower(email))
CREATE INDEX idx_tickets_open ON tickets(created) WHERE status = 'open'
```
