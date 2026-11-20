## Hint 1

Which exception does SQLite raise for a broken constraint? What does `str(exc)` look like?

## Hint 2

The message starts with the kind: `UNIQUE constraint failed`, `NOT NULL constraint failed`, `CHECK constraint failed`, `FOREIGN KEY constraint failed`. Look for the kind inside the text.

## Hint 3

```text
try: db.execute(sql); return "ok"
except sqlite3.IntegrityError as e: for kind in (...): if kind in str(e): return kind
(an IntegrityError of an unknown kind: re-raise)
```
