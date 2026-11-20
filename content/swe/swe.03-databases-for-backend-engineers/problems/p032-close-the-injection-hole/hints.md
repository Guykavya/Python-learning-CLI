## Hint 1

What is the difference between *data* and *code* in the f-string? Which characters of `name` can change the meaning of the SQL?

## Hint 2

A **placeholder** in the SQL (`:name`) reserves a place for a value; the driver sends the value separately and never interprets it as SQL.

## Hint 3

```text
conn.execute(text("SELECT id, name FROM users WHERE name = :name"), {"name": name})
return [tuple(row) for row in result]
```
