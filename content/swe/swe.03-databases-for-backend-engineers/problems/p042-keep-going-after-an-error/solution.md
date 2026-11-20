## Approach

```python
from sqlalchemy.exc import IntegrityError


def add_users(session, emails):
    skipped = []
    added = 0
    for email in emails:
        try:
            with session.begin_nested():            # a SAVEPOINT: a failure undoes only this user
                session.add(User(email=email))
            added += 1
        except IntegrityError:
            skipped.append(email)
    session.commit()
    return added, skipped
```

`begin_nested()` issues `SAVEPOINT`; when the `with` block ends, SQLAlchemy **flushes**, so the duplicate is detected right there and raised as `IntegrityError` out of the `with`. The savepoint is rolled back (only that user's insert disappears) and the outer transaction is intact, so the loop can continue and the final `commit()` saves all good users. Without the savepoint, the first `IntegrityError` rolls back the whole transaction and the next `session.add` raises `PendingRollbackError`.

Example: `["a", "b", "a", "c"]`: a, b added; the second `a` fails inside its savepoint; c is added; `(3, ["a"])`.

## Complexity

`O(n)` statements (one flush per user).

## Another way

`INSERT ... ON CONFLICT DO NOTHING` (SQLAlchemy's `insert().on_conflict_do_nothing()`) does it in one statement for bulk loads, but you do not learn which rows were skipped without extra work.

## Why it matters

"Import a batch, tell me which rows failed" is a daily task. Savepoints give you per-row failure without losing the batch (compare problem 21 with raw `sqlite3`).
