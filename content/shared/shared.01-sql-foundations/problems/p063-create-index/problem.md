# CREATE INDEX and check the plan

An index makes `WHERE` lookups on its columns fast; a *composite* index is sorted by its first column, then by the second, and so on.
A `UNIQUE` index also forbids duplicate values. `EXPLAIN QUERY PLAN <query>` tells you whether SQLite scans the table (`SCAN`) or uses an index (`SEARCH ... USING INDEX`).

The test runs your `SCRIPT` on this database (it holds a few hundred rows):

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, email TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
```

Write `SCRIPT` (only `CREATE INDEX` statements; names are up to you) so that all of this holds:

1. `SELECT * FROM orders WHERE customer_id = 7` uses an index.
2. `SELECT order_id FROM orders WHERE status = 'shipped' AND ordered >= '2024-03-01'` uses an index.
3. `SELECT order_id FROM orders WHERE customer_id = 7 ORDER BY ordered` uses an index **and** needs no extra sorting step (no `USE TEMP B-TREE FOR ORDER BY` in the plan).
4. Two customers cannot share the same `email` (`customers.email` is unique).

Use as few indexes as you can: the test accepts at most 3.

**Example**

`CREATE INDEX idx_x ON orders(status, ordered);` would solve requirement 2. Check with `EXPLAIN QUERY PLAN` that the plan now says `SEARCH orders USING INDEX idx_x (status=? AND ordered>?)`.
