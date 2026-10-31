## Hint 1

Which SQL statement does each method need (`INSERT`, `SELECT ... WHERE id = ?`, `UPDATE`, `DELETE`,
`SELECT COUNT(*)`)? Where do the values go, if not into the SQL text? And when does the data reach
the file?

## Hint 2

- In `__init__`: `self.conn.row_factory = sqlite3.Row`, then `CREATE TABLE IF NOT EXISTS ...`.
- Wrap each change in `with self.conn:`: it commits when the block ends normally and rolls back on an
  exception.
- `cursor.lastrowid` is the new id; `cursor.rowcount` is how many rows an `UPDATE` / `DELETE` changed.
- Catch `sqlite3.IntegrityError` (the `UNIQUE` rule) and `raise ValueError(...) from exc`.

## Hint 3

```
add(name, email, city):
    try:
        with self.conn:
            cur = self.conn.execute("INSERT INTO contacts (name, email, city) VALUES (?, ?, ?)", (name, email, city))
    except sqlite3.IntegrityError: raise ValueError
    return cur.lastrowid

get(id):  row = execute("SELECT * FROM contacts WHERE id = ?", (id,)).fetchone()
          return dict(row) if row else None
```

Note the one-item tuple `(id,)`: the comma makes it a tuple.
