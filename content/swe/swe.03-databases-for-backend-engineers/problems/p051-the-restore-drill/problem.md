# The restore drill

Chapter section 15.4. "Nobody wants a backup; everybody wants a **restore**." A backup is proven only when you restore it into a **fresh** place and check that the data is what you expect. Write two functions and one exception.

```python
class RestoreFailed(Exception): ...

fingerprint(conn)                                   # -> {table: {"rows": n, "sums": {column: total}}}
restore_and_verify(backup_path, expected, dest_path)
```

**`fingerprint(conn)`** describes the data of a SQLite connection compactly. For every user table (not `sqlite_*`): the number of rows, and for every column declared `INTEGER` or `REAL` the **sum** of its values (`NULL`s count as 0). Example: `{"orders": {"rows": 3, "sums": {"id": 6, "total_paise": 1500}}}`.

**`restore_and_verify(backup_path, expected, dest_path)`**:

1. If `dest_path` exists, raise `FileExistsError` (restore into a **fresh** file only).
2. Open the backup and run `PRAGMA integrity_check`. A backup that cannot be read (`sqlite3.DatabaseError`: not a database, malformed) or that fails the check raises **`RestoreFailed`**.
3. Copy it into `dest_path` with the backup API (the **restore**), compute the fingerprint of the restored database and compare it with `expected` (a fingerprint taken from the live database when the backup was made).
4. If any table differs (different row count or sums), or is missing or extra, raise `RestoreFailed` whose message **names the tables** (`tables differ after the restore: orders, users`).
5. Otherwise return the restored fingerprint.

## Example

```python
before = fingerprint(live)                   # taken at backup time
restore_and_verify("shop.bak", before, "/tmp/check.db")      # returns the fingerprint, or raises RestoreFailed
```
