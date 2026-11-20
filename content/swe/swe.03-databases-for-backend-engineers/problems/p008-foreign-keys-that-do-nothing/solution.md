## Approach

```python
import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db
```

The pragma belongs to the **connection**, not to the file: a second connection starts with foreign keys off again. That is why a single `connect` function that every part of the program uses is the only reliable fix. (The pragma is a no-op inside an open transaction, so run it right after connecting.)

Example: with it on, `INSERT INTO orders VALUES (1, 99)` for a missing customer 99 fails with `FOREIGN KEY constraint failed`.

## Complexity

`O(1)`.

## Another way

SQLAlchemy: a `connect` event listener on the engine runs the pragma for every new pooled connection (chapter section 8). PostgreSQL and MySQL (InnoDB) enforce foreign keys always.

## Why it matters

A constraint that is written but not enforced is worse than none: it makes you believe the data is safe.
