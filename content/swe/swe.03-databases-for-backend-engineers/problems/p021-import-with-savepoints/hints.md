## Hint 1

A savepoint is a named mark inside a transaction: you can go back to it without losing what was done before it. Which statements create, undo to, and release one?

## Hint 2

`SAVEPOINT name`, `ROLLBACK TO name` (the savepoint stays), `RELEASE name`. Without an outer `BEGIN`, releasing the outermost savepoint commits. Start with `db.execute("BEGIN")`.

## Hint 3

```text
db.execute("BEGIN")
for line, (sku, qty) in enumerate(rows, 1):
    SAVEPOINT row
    try INSERT; except IntegrityError: ROLLBACK TO row; errors.append((line, str(exc)))
    RELEASE row
db.commit(); return errors     (any other exception: db.rollback(); raise)
```
