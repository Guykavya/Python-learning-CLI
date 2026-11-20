## Approach

```python
from sqlalchemy import text


def lookup(engine, user_id):
    with engine.connect() as conn:                       # closed (returned to the pool) on every path
        row = conn.execute(text("SELECT name FROM users WHERE id = :id"), {"id": user_id}).first()
        if row is None:
            raise KeyError(user_id)
        return row[0]
```

`with engine.connect() as conn:` calls `conn.close()` in every case: normal exit, `return` inside the block, or an exception. "Close" on a pooled connection means **return it to the pool**, not close the database socket. `try/finally` would be equivalent; the `with` form cannot be forgotten.

Example: ten calls, five for missing users: before the fix each missing user leaked one connection, so the third missing user waited 1 s and failed; after the fix `engine.pool.checkedout()` is 0.

## Complexity

`O(1)` per call.

## Another way

`engine.begin()` (commit/rollback automatically) or a `Session` used as a context manager do the same for their resources. `pool_pre_ping` and `pool_recycle` deal with connections that die, not with leaks.

## Why it matters

A leak does not show in tests with one call. In production it shows as "everything hangs after a while" and a timeout error that points at the pool, not at the buggy line. Always acquire resources with `with`.
