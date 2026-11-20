## Approach

```python
import sqlite3
import time


def run_in_transaction(connect, work, attempts=5, sleep=time.sleep):
    for attempt in range(attempts):
        db = connect()
        try:
            result = work(db)
            db.commit()
        except sqlite3.OperationalError as exc:
            db.rollback()
            if "database is locked" not in str(exc) or attempt == attempts - 1:
                raise
            sleep(0.05 * 2 ** attempt)
        except BaseException:
            db.rollback()
            raise
        else:
            return result
        finally:
            db.close()
```

Each attempt gets a **fresh connection** and runs the **whole** unit of work again: after a lock error the transaction is rolled back, so redoing only the failed statement would be wrong. Only the "locked" error is transient; a missing table or a constraint violation will fail the same way every time, so retrying only wastes time. The `else:` branch runs only if neither `work` nor `commit` raised, so `work` is never repeated after a commit. Waiting doubles each time (backoff) so competing writers spread out.

Example: attempts 1 and 2 raise "database is locked": sleeps `0.05` and `0.1`; attempt 3 succeeds and its result is returned.

## Complexity

At most `attempts` runs of `work`.

## Another way

Set a longer `timeout` on the connection (SQLite already waits that long before raising), use `BEGIN IMMEDIATE` so that the lock is taken at the start, or use WAL mode. A retry loop is the last line of defence, and the only one that also protects against PostgreSQL's deadlock and serialization errors.

## Why it matters

Under load, transient errors are normal. A client that retries the right errors, and only those, turns them into a short delay.
