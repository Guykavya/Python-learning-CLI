# Retry when the database is locked

Chapter section 7.7. With several writers, SQLite sometimes answers `sqlite3.OperationalError: database is locked`. The right reaction is to roll back, wait a moment and **try the whole transaction again**. Write

```python
run_in_transaction(connect, work, attempts=5, sleep=time.sleep)
```

- `connect()` returns a new connection; `work(db)` does the statements of **one** transaction and may return a value.
- One attempt: `db = connect()`, `result = work(db)`, `db.commit()`, return `result`. Always `close()` the connection at the end of the attempt.
- If an attempt raises `sqlite3.OperationalError` whose message contains `database is locked`: `rollback()`, wait `sleep(0.05 * 2**k)` (`k = 0` after the first failed attempt, 1 after the second, ...) and try again, at most `attempts` attempts in all. After the last attempt re-raise the error (no sleep).
- **Any other exception** (a `ValueError` from your own code, an `OperationalError` such as `no such table`, an `IntegrityError`): `rollback()` and re-raise **at once**, without retrying.
- **Never run `work` again after a successful commit.** A transaction that committed is done.
- The tests use fake connections that record `commit`, `rollback` and `close`, and a fake `sleep`.

## Example

```python
# work fails twice with "database is locked", then succeeds
run_in_transaction(connect, work, attempts=5, sleep=waits.append)    # the result of work; waits == [0.05, 0.1]
```
