# Trace: what is left after ROLLBACK and SAVEPOINT

A *transaction* groups statements so that they all take effect (`COMMIT`) or none do (`ROLLBACK`). A `SAVEPOINT` marks a point inside a transaction;
`ROLLBACK TO name` undoes everything after that point but keeps the transaction open; `RELEASE name` just forgets the savepoint (its changes stay). A statement
that **fails** (for example a `CHECK` violation) is undone by itself, and the transaction stays open.

This program runs the statements one by one on an empty in-memory database in "manual" mode (`isolation_level=None`, so only your `BEGIN`/`COMMIT` start and end transactions).
A failing statement is printed and skipped; the loop goes on.

```python
import sqlite3

STATEMENTS = [
    'CREATE TABLE acct (id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER NOT NULL CHECK (balance >= 0))',
    "INSERT INTO acct VALUES (1,'Ada',100),(2,'Bo',50)",
    'BEGIN',
    'UPDATE acct SET balance = balance - 30 WHERE id = 1',
    'SAVEPOINT s1',
    'UPDATE acct SET balance = balance + 30 WHERE id = 2',
    "INSERT INTO acct VALUES (3,'Cy',10)",
    'ROLLBACK TO s1',
    "INSERT INTO acct VALUES (4,'Di',5)",
    'SAVEPOINT s2',
    'DELETE FROM acct WHERE id = 2',
    'RELEASE s2',
    'COMMIT',
    'BEGIN',
    'UPDATE acct SET balance = 0 WHERE id = 1',
    "INSERT INTO acct VALUES (5,'Eve',1)",
    'ROLLBACK',
    'BEGIN',
    'UPDATE acct SET balance = balance - 500 WHERE id = 1',
    'UPDATE acct SET balance = balance + 1 WHERE id = 1',
    'COMMIT',
]

con = sqlite3.connect(":memory:", isolation_level=None)
for sql in STATEMENTS:
    try:
        con.execute(sql)
    except sqlite3.Error as e:
        print("error:", e)          # the error text is NOT part of your answer
rows = con.execute("SELECT id, owner, balance FROM acct ORDER BY id").fetchall()
```

What does the final `SELECT` return?

Write your answer in `answer.txt`: one line per result row, column values joined with `|` (no spaces), `NULL` for a NULL,
no header line, strings without quotes. If the query returns no rows, write the single line `(no rows)`.

**Example (a different script)**

```sql
CREATE TABLE t (x INTEGER);
BEGIN; INSERT INTO t VALUES (1); COMMIT;
BEGIN; INSERT INTO t VALUES (2); ROLLBACK;
SELECT x FROM t;   -- one line: 1
```
