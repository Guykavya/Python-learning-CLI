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
            with self.conn:                          # commit on success, rollback on error
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
