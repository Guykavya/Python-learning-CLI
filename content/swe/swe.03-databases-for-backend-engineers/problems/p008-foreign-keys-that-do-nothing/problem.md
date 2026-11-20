# Foreign keys that do nothing

In SQLite, `REFERENCES` clauses are **ignored** unless every connection runs `PRAGMA foreign_keys = ON` (chapter section 4.4). The setting is per connection and is off by default. Orphan rows (an order for a customer that does not exist) slip in silently.

`starter.py` has a `connect(path)` function that forgets the pragma. Fix it so that:

- the returned `sqlite3.Connection` has foreign keys **on** (`PRAGMA foreign_keys` returns `1`);
- it waits up to 5 seconds when the database is locked (`timeout=5`);
- it works for `":memory:"` and for file paths.

## Example

```python
db = connect(":memory:")
db.execute("PRAGMA foreign_keys").fetchone()    # (1,)
```

The tests insert an order for a missing customer and expect `sqlite3.IntegrityError`.
