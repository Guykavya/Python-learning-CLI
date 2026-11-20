## Hint 1

Is the setting stored in the database file, or in the connection? What does that mean for code that opens a connection in ten places?

## Hint 2

The pragma is a normal statement: `db.execute("PRAGMA foreign_keys = ON")`. When must it run: before or after your first write?

## Hint 3

```text
db = sqlite3.connect(path, timeout=5)
db.execute("PRAGMA foreign_keys = ON")
return db
```
