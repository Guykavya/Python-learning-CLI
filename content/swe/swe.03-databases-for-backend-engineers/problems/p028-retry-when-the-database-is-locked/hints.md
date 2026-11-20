## Hint 1

A retry loop has three outcomes per attempt: success (return), a failure worth retrying (wait and loop) and a failure not worth retrying (raise). Which failures are worth it?

## Hint 2

Decide with the **text** of the error, and only for `OperationalError`. Remember to roll back before sleeping (so the lock is released) and to close the connection in every case.

## Hint 3

```text
for attempt in range(attempts):
    db = connect()
    try: result = work(db); db.commit()
    except OperationalError as e: rollback; if not locked or last attempt: raise; sleep(0.05 * 2**attempt)
    except BaseException: rollback; raise
    else: return result
    finally: db.close()
```
