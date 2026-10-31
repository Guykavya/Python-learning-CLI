## Approach

The class owns one connection. The constructor sets `row_factory` (rows become dict-like) and creates
the table only if it is missing, so reopening a file keeps its data.

Every value goes through a `?` placeholder. The SQL text is constant, the values travel separately and
are never parsed as SQL, which removes both the "quote breaks my query" bug and SQL injection.

Every change runs inside `with self.conn:`. The connection's context manager **does not close** the
connection: it commits if the block succeeds and rolls back if an exception escapes. A failed
`INSERT` (duplicate email) is therefore undone, and the next insert works normally. The
`IntegrityError` is translated into a `ValueError`, so callers do not need to know that sqlite3 is
used inside.

## Code

```python
import sqlite3


class ContactBook:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        with self.conn:
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS contacts ("
                " id INTEGER PRIMARY KEY,"
                " name TEXT NOT NULL,"
                " email TEXT NOT NULL UNIQUE,"
                " city TEXT)"
            )

    def add(self, name, email, city=None):
        try:
            with self.conn:
                cur = self.conn.execute(
                    "INSERT INTO contacts (name, email, city) VALUES (?, ?, ?)",
                    (name, email, city),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"email {email!r} is already used") from exc
        return cur.lastrowid

    def get(self, contact_id):
        row = self.conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return dict(row) if row is not None else None

    def find_by_city(self, city):
        rows = self.conn.execute(
            "SELECT * FROM contacts WHERE city = ? ORDER BY name", (city,)
        ).fetchall()
        return [dict(row) for row in rows]

    def update_email(self, contact_id, email):
        try:
            with self.conn:
                cur = self.conn.execute(
                    "UPDATE contacts SET email = ? WHERE id = ?", (email, contact_id)
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"email {email!r} is already used") from exc
        return cur.rowcount == 1

    def delete(self, contact_id):
        with self.conn:
            cur = self.conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        return cur.rowcount == 1

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
```

## Complexity

`get`, `update_email` and `delete` use the primary key index: O(log n). `find_by_city` scans the table,
O(n) plus sorting; `CREATE INDEX idx_city ON contacts(city)` would make it O(log n + k).

## Another way

Named placeholders read better when there are many values:
`execute("INSERT INTO contacts (name, email, city) VALUES (:name, :email, :city)", {"name": ..., ...})`.
And `executemany(sql, list_of_tuples)` inserts many rows in one call (and one transaction), much faster
than a loop of single inserts that each commit.
