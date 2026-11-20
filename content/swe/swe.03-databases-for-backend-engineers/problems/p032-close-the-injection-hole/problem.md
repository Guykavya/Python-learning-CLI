# Close the injection hole

Chapter section 8.5. `starter.py` finds a user by name:

```python
def find_user(conn, name):
    return list(conn.exec_driver_sql(f"SELECT id, name FROM users WHERE name = '{name}'"))
```

The name is pasted **into the SQL text**. `find_user(conn, "' OR 1=1 --")` returns every user, and `find_user(conn, "O'Brien")` crashes with a syntax error. Rewrite `find_user(conn, name)` with a **bound parameter**:

- use `sqlalchemy.text("SELECT id, name FROM users WHERE name = :name")` and pass `{"name": name}`;
- return a **list of tuples** `(id, name)`;
- the name must never appear in the SQL text that reaches the database: it travels separately as a parameter (the tests check the statements with an event listener).

## Example

```python
find_user(conn, "Asha")           # [(1, "Asha")]
find_user(conn, "O'Brien")        # [(2, "O'Brien")]
find_user(conn, "' OR 1=1 --")    # []
```
