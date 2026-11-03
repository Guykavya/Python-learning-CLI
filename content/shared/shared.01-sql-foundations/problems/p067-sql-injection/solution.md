## Approach

Use the model answer in `answer.md`: injection means user input gets parsed as SQL because it was glued into the statement text. Parameters keep the statement text and the values separate, so a value can never become syntax. But only *values* can be parameters, not names of tables or columns, so identifiers must come from an allow-list.

## Code

```python
ALLOWED = {"title", "price", "published"}

def top(con, column, n):
    if column not in ALLOWED:
        raise ValueError("bad column")
    return con.execute(f"SELECT title, {column} FROM books ORDER BY {column} LIMIT ?", (n,)).fetchall()
```

## Complexity

No cost difference: the statement is parsed once either way. (Parameters even help: a statement with placeholders can be compiled once and reused with different values.)

## Another way / portable SQL

Every driver has placeholders (`?` in sqlite3, `%s` in psycopg and MySQL connectors). Stored procedures and ORMs use the same mechanism underneath. Quoting identifiers (`"name"` in SQLite/PostgreSQL, backticks in MySQL) is *not* a defence by itself; use an allow-list.
