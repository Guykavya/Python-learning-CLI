## Approach

```python
import sqlite3


def buy(path, product_id):
    db = sqlite3.connect(path, timeout=10)
    try:
        with db:
            cur = db.execute("UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0", (product_id,))
            if cur.rowcount == 0:
                return False
            db.execute("INSERT INTO sales(product_id) VALUES (?)", (product_id,))
            return True
    finally:
        db.close()
```

The check (`stock > 0`) and the change (`stock - 1`) happen inside **one** statement, so no other connection can slip in between: SQLite runs writers one after the other. `rowcount` says whether the guard held. The sale is recorded in the same transaction, so `sales` and `stock` always agree, and `timeout=10` makes a busy writer wait instead of failing at once with "database is locked".

Example: with stock 1 and two buyers, the first `UPDATE` changes 1 row (stock 0) and returns `True`; the second finds `stock > 0` false, changes 0 rows and returns `False`.

## Complexity

`O(1)` per call.

## Another way

`SELECT ... FOR UPDATE` (PostgreSQL) locks the row for the whole read-modify-write; optimistic locking with a version column (problem 25) detects the clash and retries. The atomic `UPDATE` is the simplest and the fastest when the change is a simple expression.

## Why it matters

The read-modify-write bug passes every single-user test and loses money in production. The only reliable detection is a test with threads, like this one.
