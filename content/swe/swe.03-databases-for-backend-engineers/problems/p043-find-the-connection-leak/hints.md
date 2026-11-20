## Hint 1

On which path does the program leave the function without closing the connection? How many such paths are there?

## Hint 2

`with engine.connect() as conn:` closes the connection when the block ends, however it ends (return, exception). That is the purpose of a context manager.

## Hint 3

```text
with engine.connect() as conn:
    row = conn.execute(...).first()
    if row is None: raise KeyError(user_id)
    return row[0]
```
