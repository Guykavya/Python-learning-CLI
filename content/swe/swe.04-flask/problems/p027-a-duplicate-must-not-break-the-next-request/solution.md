## Approach

Add one line to the `except` branch:

```python
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()                      # the session is usable again
    taken = set(db.session.scalars(db.select(User.username).where(User.username.like(username + "%"))))
    ...
    return jsonify(error=f"username {username!r} is taken", suggestions=suggestions), 409
```

Example: with the starter, the `SELECT` for the suggestions raises `PendingRollbackError: This Session's transaction has been rolled back due to a previous exception during flush`. The visitor gets a 500 instead of a friendly 409, and in a long-lived app context the **next** request fails too.

Why does the session survive? Flask-SQLAlchemy's `db.session` is a *scoped* session tied to the **app context**. In production each request has its own context, which is removed at the end. In tests that wrap everything in `with app.app_context():` (or code that reuses one context for a batch job) there is only one session for many requests, and one failure poisons all of them. Rolling back where the error happens makes the code correct in both situations.

Also note: the duplicate is detected **by the database** (`UNIQUE`), not by a `SELECT` before the insert. A check-then-insert has a race (two requests check at the same moment, both see "free"); the constraint cannot be raced.

## Complexity

`O(1)` for the insert; `O(k)` for the suggestions, where `k` is the number of existing names that share the prefix.

## Another way

Check first (`SELECT`) for a friendly message **and** keep the `except IntegrityError` for the race: a belt and braces solution.

## Not covered

Deadlocks and retries (swe.03).
