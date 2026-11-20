# Scan or search?

Chapter section 5.3. `EXPLAIN QUERY PLAN` tells how SQLite will run a query. Each row of the answer is `(id, parent, notused, detail)`, and `detail` starts with **`SCAN`** (reads every row: slow on big tables) or **`SEARCH`** (jumps to the rows through an index or the primary key: fast).

Write

```python
uses_index(db, sql, params=())
```

returning `True` if **any** plan row of the query contains the word `SEARCH`, and `False` otherwise. Do not run the query itself, only its plan. The wording of plans changes between SQLite versions (`SCAN TABLE t` became `SCAN t`), so look only for the word.

## Example

```python
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT)")
db.execute("CREATE INDEX idx_email ON users(email)")
uses_index(db, "SELECT * FROM users WHERE email = ?", ("a@x.com",))   # True  (SEARCH ... USING INDEX idx_email)
uses_index(db, "SELECT * FROM users WHERE city = ?", ("Pune",))       # False (SCAN)
uses_index(db, "SELECT * FROM users WHERE id = 5")                    # True  (SEARCH ... INTEGER PRIMARY KEY)
```
