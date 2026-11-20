# Which constraint said no?

Chapter section 4.2. Write

```python
attempt(db, sql)
```

that executes one SQL statement on the SQLite connection `db` and returns:

- `"ok"` if it worked;
- `"UNIQUE"`, `"NOT NULL"`, `"CHECK"` or `"FOREIGN KEY"` if SQLite raised `sqlite3.IntegrityError`, chosen from the **message** of the error (for example `UNIQUE constraint failed: users.email`). A duplicate primary key also reports `UNIQUE`.

Other errors (a syntax error, a missing table) are **not** constraint problems: let them propagate. If the statement fails, the connection must remain usable and **nothing of that statement stays** in the table.

## Example

```python
attempt(db, "INSERT INTO users(email) VALUES ('a@x.com')")   # "ok"
attempt(db, "INSERT INTO users(email) VALUES ('a@x.com')")   # "UNIQUE"
attempt(db, "INSERT INTO users(email) VALUES (NULL)")        # "NOT NULL"
```
