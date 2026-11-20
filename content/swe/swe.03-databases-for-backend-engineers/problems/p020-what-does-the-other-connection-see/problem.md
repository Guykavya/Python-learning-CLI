# What does the other connection see?

Chapter section 6.4. Two connections, `a` and `b`, use the **same database file**. In Python's `sqlite3`, an `INSERT`/`UPDATE`/`DELETE` starts a transaction automatically; a `SELECT` does not. Each connection waits at most 0.2 seconds for a lock.

```python
import sqlite3, tempfile, os
path = os.path.join(tempfile.mkdtemp(), "t.db")

a = sqlite3.connect(path, timeout=0.2)
b = sqlite3.connect(path, timeout=0.2)
a.execute("CREATE TABLE t (x INTEGER)")
a.execute("INSERT INTO t VALUES (1)")
a.commit()
print("1:", b.execute("SELECT x FROM t").fetchall())
a.execute("UPDATE t SET x = 2")
print("2:", a.execute("SELECT x FROM t").fetchall())
print("3:", b.execute("SELECT x FROM t").fetchall())
a.commit()
print("4:", b.execute("SELECT x FROM t").fetchall())
a.execute("UPDATE t SET x = 3")
a.rollback()
print("5:", a.execute("SELECT x FROM t").fetchall())
print("6:", b.execute("SELECT x FROM t").fetchall())
b.execute("INSERT INTO t VALUES (9)")
try:
    a.execute("INSERT INTO t VALUES (10)")
    print("7: ok")
except sqlite3.OperationalError as e:
    print("7:", e)
b.commit()
a.execute("INSERT INTO t VALUES (10)")
a.commit()
print("8:", b.execute("SELECT x FROM t ORDER BY x").fetchall())
```

Predict **exactly** what the program prints (eight lines). A row is printed as `[(value,)]`. For line 7, the program prints the **text of the error** if there is one, or `ok`. Do not run it.

Write your answer in `answer.txt`.

## How to work

1. Keep two lists for the table: what is **committed** (everyone sees it) and what connection `a` or `b` has changed but not committed (only that connection sees it).
2. A connection that has written holds the **write lock** until it commits or rolls back; another connection that wants to write must wait (and fails after its timeout).
3. In the default (rollback-journal) mode readers keep seeing the last committed data while someone else writes.

## After you answer

1. Why does line 2 show `[(2,)]` and line 3 show `[(1,)]` for the same table at the same moment?
2. What does `rollback()` do to the `UPDATE ... SET x = 3`, and what do lines 5 and 6 show?
3. Why can connection `a` not insert in line 7, and what has to happen before it can?
