# executemany, row_factory and closing connections

Three tools you will use in every program that talks to SQLite:

- `con.executemany(sql, list_of_tuples)` runs one statement many times with different parameters (much faster than a Python loop of `execute`).
- `con.row_factory = sqlite3.Row` makes rows behave like read-only dicts (`row["title"]`); `dict(row)` converts one.
- `with con:` commits or rolls back, but does **not** close the connection. To close it, use `contextlib.closing(sqlite3.connect(...))`.

Table:

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL CHECK (price > 0));
```

Write in `solution.py`:

1. `add_books(con, rows)`: `rows` is a list of `(title, category, price)` tuples. Insert them all with **one** `executemany`, inside a transaction, and return how many were inserted. If any row is invalid (for example a price of 0), **none** of the rows may be inserted and the `sqlite3.IntegrityError` must propagate.
2. `books_as_dicts(con, category)`: return a list of dicts `{"title": ..., "price": ...}` for that category, ordered by title. Use `sqlite3.Row`, but restore the connection's original `row_factory` before returning (even if the query fails).
3. `average_by_category(db_path)`: open its own connection to the file `db_path`, return `{category: average price rounded to 2 decimals}`, and **close** the connection before returning, also when an error happens.

**Example**

```python
add_books(con, [("A", "Tech", 10), ("B", "Tech", 20)])        # returns 2
add_books(con, [("C", "Tech", 5), ("D", "Tech", 0)])          # raises IntegrityError; C is NOT inserted
books_as_dicts(con, "Tech")        # [{"title": "A", "price": 10.0}, {"title": "B", "price": 20.0}]
```
