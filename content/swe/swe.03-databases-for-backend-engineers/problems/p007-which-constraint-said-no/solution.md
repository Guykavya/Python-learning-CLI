## Approach

```python
import sqlite3

KINDS = ("UNIQUE", "NOT NULL", "CHECK", "FOREIGN KEY")


def attempt(db, sql):
    try:
        db.execute(sql)
    except sqlite3.IntegrityError as exc:
        for kind in KINDS:
            if kind in str(exc):
                return kind
        raise
    return "ok"
```

Only `IntegrityError` is caught: a typo in the SQL is a bug, not a constraint, and must not be hidden. A single failed statement does not corrupt the table: SQLite undoes the statement.

Example: the second insert of `a@x.com` raises `IntegrityError: UNIQUE constraint failed: users.email`, so the function returns `"UNIQUE"`.

## Complexity

`O(1)` besides the statement.

## Another way

PostgreSQL gives machine-readable codes (`23505` unique, `23502` not null, `23503` foreign key, `23514` check); parsing English messages is the SQLite way, and fragile across versions.

## Why it matters

An API turns these errors into `409 Conflict` or `422` answers (swe.07); knowing which constraint fired is how it chooses.
