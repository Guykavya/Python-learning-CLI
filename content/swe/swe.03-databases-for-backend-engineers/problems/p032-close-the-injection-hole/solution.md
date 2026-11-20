## Approach

```python
from sqlalchemy import text


def find_user(conn, name):
    result = conn.execute(text("SELECT id, name FROM users WHERE name = :name"), {"name": name})
    return [tuple(row) for row in result]
```

`text()` turns `:name` into the driver's placeholder (`?` for SQLite). The database receives the **statement** and the **value** separately: whatever the value contains, it is only ever compared as a string. The quote in `O'Brien` is just a character, and `' OR 1=1 --` is looked up as a (non-existent) name.

Example: the statement that reaches SQLite is `SELECT id, name FROM users WHERE name = ?` with the parameters `("O'Brien",)`.

## Complexity

One indexed or full lookup.

## Another way

Core constructors (`select(users).where(users.c.name == name)`) bind automatically. Use `text()` for hand-written SQL, always with `:name` parameters.

## Why it matters

SQL injection is still among the top causes of data breaches, and the fix has been known for decades: **never build SQL from user input; bind it**.
