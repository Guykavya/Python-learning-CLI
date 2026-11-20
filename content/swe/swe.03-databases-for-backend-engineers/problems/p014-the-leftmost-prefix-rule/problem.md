# The leftmost-prefix rule

Chapter section 5.6. A table has one composite index:

```sql
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INT, status TEXT, created TEXT, total INT);
CREATE INDEX idx ON orders(customer_id, status, created);
```

An index on `(a, b, c)` is a list sorted by `a`, then `b`, then `c`. The database can use it only from the **left**: first `a`, then `b` (if `a` was compared with `=`), then `c`. A range comparison (`>`, `<`) on a column stops the chain: the columns after it cannot be used to narrow the search.

For each `WHERE` clause below decide how much of the index a search uses:

- `full`: all three columns narrow the search;
- `partial`: the index is used (a `SEARCH`) but only for the first one or two columns, the rest is filtered afterwards;
- `no`: the index is not used for searching (the table is scanned).

```text
1. WHERE customer_id = 1 AND status = 'open' AND created > '2026-01-01'
2. WHERE customer_id = 1 AND status = 'open'
3. WHERE customer_id = 1
4. WHERE status = 'open'
5. WHERE customer_id = 1 AND created > '2026-01-01'
6. WHERE status = 'open' AND created > '2026-01-01'
7. WHERE customer_id = 1 AND status > 'a' AND created > '2026-01-01'
8. WHERE customer_id IN (1, 2) AND status = 'open' AND created > '2026-01-01'
```

Write your answer in `answer.txt`, one line per clause: `1: full`, `2: partial`, and so on. In clause 2 only two columns are given, so it is `partial` (not all three narrow the search). Do not run anything.

## After you answer

1. Why does clause 5 skip `status` and only use `customer_id`?
2. Why does clause 7 stop at `status`?
3. What index would make clause 4 a search?
