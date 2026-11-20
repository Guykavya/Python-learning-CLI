## Hint 1

Between "is there enough stock?" and "take it", what must not be able to happen? Which kind of lock prevents it?

## Hint 2

A plain `BEGIN` is deferred: the lock comes at the first write, after your read. `BEGIN IMMEDIATE` takes the write lock first. Any exception after that must end with `rollback()`.

## Hint 3

```text
db.execute("BEGIN IMMEDIATE")
try: read stock; checks; INSERT order; UPDATE stock
except: db.rollback(); raise
db.commit(); return the order id
```
