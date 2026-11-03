# Explain: SQL injection and what parameters cannot do

A junior developer wrote this login check:

```python
def login(con, name, password):
    sql = f"SELECT id, name FROM users WHERE name = '{name}' AND password = '{password}'"
    return con.execute(sql).fetchall()
```

Data: `users` has `(1, 'ada', 's3cret')` and `(2, 'bo', 'hunter2')`. Real results of calling it (SQLite, from a test run):

```
login("ada", "wrong")
SQL:    SELECT id, name FROM users WHERE name = 'ada' AND password = 'wrong'
result: []

login("ada' --", "anything")
SQL:    SELECT id, name FROM users WHERE name = 'ada' --' AND password = 'anything'
result: [(1, 'ada')]

login("x", "' OR '1'='1")
SQL:    SELECT id, name FROM users WHERE name = 'x' AND password = '' OR '1'='1'
result: [(1, 'ada'), (2, 'bo')]
```

Then the fixed version:

```python
con.execute("SELECT id, name FROM users WHERE name = ? AND password = ?", (name, password))
```

With `name = "ada' --"` and `password = "anything"` this returns `[]`.

Answer in your own words (150-400 words):

1. What exactly went wrong in the second call? Trace how the text of the SQL changed.
2. Why does the `?` version return `[]` for the same input? What is different about how the database receives the value?
3. A teammate then wants `def top(con, column, n): con.execute("SELECT ? FROM books ORDER BY ? LIMIT ?", (column, column, n))` so users can pick the sort column. Does it work? (Hint: in SQLite, `SELECT ? FROM users` with `"name"` returns the text `'name'` for every row.) What should be done instead?
4. Name two other defences besides parameters.

Write your answer in `answer.md`, then compare with the model answer.
