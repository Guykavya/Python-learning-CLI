## Approach

`with con:` wraps the `executemany` in a transaction: all rows or none. `len(rows)` is the count. For dictionaries, temporarily switch `row_factory`, convert each row with `dict(row)`, and restore the old factory in a `finally`. For the file connection use `closing(...)`, which calls `.close()` on exit.

## Code

```python
import sqlite3
from contextlib import closing


def add_books(con, rows):
    with con:
        con.executemany("INSERT INTO books (title, category, price) VALUES (?, ?, ?)", rows)
    return len(rows)


def books_as_dicts(con, category):
    old = con.row_factory
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute("SELECT title, price FROM books WHERE category = ? ORDER BY title", (category,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        con.row_factory = old


def average_by_category(db_path):
    with closing(sqlite3.connect(db_path)) as con:
        cur = con.execute("SELECT category, ROUND(AVG(price), 2) FROM books GROUP BY category")
        return dict(cur.fetchall())
```

## Complexity

`executemany` prepares the statement once and runs it n times: O(n log n) with one commit, instead of n commits (each commit is a disk sync, usually the slowest part).

## Another way / portable SQL

`cur.rowcount` after `executemany` also gives the count of inserted rows. Use `con.row_factory = lambda cur, row: dict(zip([c[0] for c in cur.description], row))` to get plain dicts. In PostgreSQL (`psycopg`) you use `executemany` or `COPY` for bulk loading and `cursor_factory=DictCursor` for dict rows.
