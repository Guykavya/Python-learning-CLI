## Hint 1

What does `g` hold between the start and the end of one request? How can you ask "is there already a connection in `g`?" without an error when there is none?

## Hint 2

`"db" not in g` works (g supports `in`), and `g.pop("db", None)` removes the attribute and returns it (or `None`). `close_db` is called with the exception (or `None`) by `teardown_appcontext`, whatever happened.

## Hint 3

```text
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"]); set row_factory
    return g.db

def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None: db.close()
```
