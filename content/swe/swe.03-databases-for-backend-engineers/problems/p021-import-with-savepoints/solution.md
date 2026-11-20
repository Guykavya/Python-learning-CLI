## Approach

```python
import sqlite3


def import_rows(db, rows):
    errors = []
    db.execute("BEGIN")
    try:
        for line, (sku, qty) in enumerate(rows, 1):
            db.execute("SAVEPOINT row")
            try:
                db.execute("INSERT INTO products(sku, qty) VALUES (?, ?)", (sku, qty))
            except sqlite3.IntegrityError as exc:
                db.execute("ROLLBACK TO row")
                errors.append((line, str(exc)))
            db.execute("RELEASE row")
    except BaseException:
        db.rollback()
        raise
    db.commit()
    return errors
```

The outer `BEGIN` makes **one** transaction for the whole import. Inside it every row has a savepoint: if the insert fails, `ROLLBACK TO row` removes only that row's effects; `RELEASE row` closes the savepoint in both cases. Only `IntegrityError` is treated as "bad row"; a different exception means the program or the database is broken, so everything is rolled back and the error continues upward. One `commit()` at the end is fast (one disk sync, not one per row).

Example: rows `("a", 5), ("a", 2), ("b", 0), ("c", 7)`: row 2 violates `UNIQUE`, row 3 violates `CHECK`; rows 1 and 4 are inserted and committed together.

## Complexity

`O(rows)`, one commit.

## Another way

Insert everything with `INSERT OR IGNORE` and compare counts: you lose the reason for each rejection.

## Why it matters

Imports of messy data must report **which** rows failed and why, without losing the good ones and without a commit per row (which is hundreds of times slower).
