## Approach

```python
INDEXES = [
    "CREATE INDEX idx_users_email_lower ON users(lower(email))",
    "CREATE INDEX idx_tickets_open ON tickets(created) WHERE status = 'open'",
]
```

An **expression index** stores the value of an expression for every row. A query can use it only when it contains the **same expression** (`lower(email)`; the spelling of the function name does not matter, but `email COLLATE NOCASE` is a different thing). A **partial index** stores only the rows for which its `WHERE` is true: here 1% of the tickets, so it is small and cheap to maintain, and it is sorted by `created`, so the `ORDER BY` costs nothing. SQLite uses it only if the query's `WHERE` implies the index's `WHERE` (`status = 'open'` does; `status = 'closed'` does not).

Example plan of Q2: `SCAN tickets USING COVERING INDEX idx_tickets_open` (SQLite reads the whole small index in order) and no `TEMP B-TREE`. The query for closed tickets gets `SCAN tickets` and a `TEMP B-TREE`.

## Complexity

`O(log n)` lookups.

## Another way

Store a lower-cased copy of the e-mail in its own column and index that. PostgreSQL supports both forms; MySQL needs a generated column for the first.

## Why it matters

A good index is often **smaller**: the partial index here is 100 times smaller than a full one, so it stays in memory and slows writes only for open tickets.
