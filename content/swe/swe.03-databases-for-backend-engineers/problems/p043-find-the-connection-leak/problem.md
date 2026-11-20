# Find the connection leak

Chapter section 12.4. An engine keeps a **pool** of connections: `QueuePool(pool_size=2, max_overflow=0)` allows two connections at the same time. A connection taken with `engine.connect()` must be **returned** (`close()`); a connection that is never returned is a **leak**, and when all of them are leaked, the next request waits for `pool_timeout` seconds and then fails with `TimeoutError`.

`starter.py` has

```python
def lookup(engine, user_id):
    conn = engine.connect()
    row = conn.execute(text("SELECT name FROM users WHERE id = :id"), {"id": user_id}).first()
    if row is None:
        raise KeyError(user_id)
    conn.close()
    return row[0]
```

When the user does not exist it raises **before** `conn.close()`: the connection is lost. After two such calls the pool is empty and the third call hangs for the pool timeout.

Fix `lookup` so that the connection is **always** returned, on success and on error (hint: let a `with` statement do it), and keep the behaviour: return the name, or raise `KeyError(user_id)`.

The test creates `create_engine(url, poolclass=QueuePool, pool_size=2, max_overflow=0, pool_timeout=1)` on a file database, makes 10 calls (half of them for missing users) and checks that `engine.pool.checkedout() == 0` at the end.
