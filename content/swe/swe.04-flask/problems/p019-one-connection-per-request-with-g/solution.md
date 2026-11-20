## Approach

`g` is the scratch space of the **current app context**, created for each request and thrown away at its end, so it is the right place for "the connection of this request".

```python
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
```

and in the factory: `app.teardown_appcontext(close_db)`.

Example: `GET /` never calls `get_db()`, so `"db" not in g` stays true and nothing is opened. `GET /count` calls it three times: the first call opens and stores, the next two return the stored object. At the end of the request Flask pops the app context and calls `close_db`, even if the view raised.

Why lazily? A connection costs time and (for server databases) a slot in a limited pool. Pages that do not need the database should not pay for one.

## Complexity

`O(1)` per call; one connection per request.

## Another way

Flask-SQLAlchemy (section 14) does exactly this for you: `db.session` is created on first use and removed at teardown. Knowing the manual version explains what the extension does and what a "connection leak" is.

## Not covered

Connection pools: opening a connection for every request is fine for SQLite; for PostgreSQL you use a pool (swe.03) so a request borrows a connection instead of creating one.
