# A duplicate must not break the next request

Chapter section 14.7. After a failed `commit()` (for example a `UNIQUE` violation) the SQLAlchemy session is in a **"needs rollback"** state: every further use raises `PendingRollbackError` until you call `db.session.rollback()`.

In `solution.py` the starter has `db`, the model `User` (`username` is unique) and the view `POST /register` with JSON `{"username": "asha"}`:

- Invalid name (not a string of 3 to 20 characters from `a-z 0-9 _`, after stripping) → **400** `{"error": "..."}`.
- Success → **201** `{"id", "username"}`.
- A name that is **already taken** → **409** and JSON
  `{"error": "username 'asha' is taken", "suggestions": ["asha1", "asha2"]}`.
  The suggestions are the **first two** names of the form `<name>1`, `<name>2`, `<name>3`, ... that are **not yet in the database**, so building them means querying the database **after the failed commit**.

The starter catches the `IntegrityError` but forgets the rollback, so the query for the suggestions fails. A second trap: if the test client runs inside an outer `with app.app_context():` (as many test suites do), the session is **not** removed between requests, so the broken session also kills the **next** request.

Fix the view. Do not change the model.

## Example

```text
POST /register {"username": "asha"}   -> 201
POST /register {"username": "asha"}   -> 409 {"error": "username 'asha' is taken", "suggestions": ["asha1", "asha2"]}
POST /register {"username": "ravi"}   -> 201     (must still work afterwards)
```
