# One connection per request with `g`

Chapter sections 10.3 and 10.4. A web app needs a database connection **per request**: not one per query (slow), not one global (shared between threads), and never left open. The Flask pattern is: open **lazily** on first use, keep it in `g`, close it when the request ends.

In `solution.py` the starter has `init_db(path)` and the routes. Write the two functions:

- `get_db()`: returns the connection stored in `g.db`. The **first** call in a request opens it with `sqlite3.connect(current_app.config["DATABASE"])` and sets `row_factory = sqlite3.Row`; later calls in the same request return the **same** object.
- `close_db(exc=None)`: registered with `app.teardown_appcontext`. Closes the connection if one was opened, and does nothing if none was (a page that never touched the database must not open one just to close it). It must also run when the view **raised**.

The tests replace `sqlite3.connect` with a counting wrapper, so they can tell **how many connections were opened and closed** in each request: the page `/` (no database) must open **0**, the page `/count` (which calls `get_db()` three times) must open **exactly 1**, and every connection opened must be closed.

## Example

```text
GET /        -> opened 0, closed 0
GET /count   -> opened 1, closed 1      (get_db() called 3 times, one connection)
GET /boom    -> 500, opened 1, closed 1 (the view raised after using the database)
```
