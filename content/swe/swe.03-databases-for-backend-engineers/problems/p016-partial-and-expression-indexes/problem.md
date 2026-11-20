# Partial and expression indexes

Chapter section 5.7. Two queries, two special cases:

```sql
CREATE TABLE users   (id INTEGER PRIMARY KEY, email TEXT NOT NULL, name TEXT NOT NULL);
CREATE TABLE tickets (id INTEGER PRIMARY KEY, created TEXT NOT NULL, status TEXT NOT NULL, subject TEXT NOT NULL);

-- Q1: log in with an e-mail typed in any case
SELECT id FROM users WHERE lower(email) = ?;
-- Q2: the open tickets, oldest first (only 1% of tickets are open)
SELECT id FROM tickets WHERE status = 'open' ORDER BY created;
```

Write `INDEXES`, a list of **exactly two** `CREATE INDEX` statements:

1. an **expression index** that makes Q1 a `SEARCH`;
2. a **partial index** (`... WHERE status = 'open'`) that Q2 **uses** (the plan says `USING ... INDEX` and, because the whole small index is read in order, it may say `SCAN ... USING COVERING INDEX`) **and** that removes the sort (no `TEMP B-TREE`), and that is **small**: it must contain only the open tickets.

The tests check the plans, the text of your index definitions, and that a query for `status = 'closed'` does **not** use the partial index.
