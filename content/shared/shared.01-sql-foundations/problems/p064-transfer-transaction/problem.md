# transfer() with a transaction and rollback

A money transfer is two updates: take from one account, give to another. If the second one fails after the first one worked, money vanishes.
A transaction fixes that: either both updates are saved or neither is.

In Python's `sqlite3`, `with con:` opens a transaction on the first change and, when the block ends, **commits** if there was no exception or **rolls back** if there was one.
(It does *not* close the connection.)

The database has this table:

```sql
CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER NOT NULL CHECK (balance >= 0));
```

Write `transfer(con, source, target, amount)` that moves `amount` from account `source` to account `target`, with these rules:

- `amount` must be a positive integer and `source` and `target` must differ, otherwise raise `ValueError`.
- If either account id does not exist, raise `KeyError` (with the missing id).
- If the source balance is smaller than `amount`, raise `ValueError` (not `sqlite3.IntegrityError`).
- After **any** failure both balances are exactly what they were before, and the connection has no open transaction left.
- After success the change is committed (another connection to the same file sees it).
- Use `?` parameters, never f-strings in SQL. Return `None`.

**Example**

```python
# accounts: (1, 'Ada', 100), (2, 'Bo', 50)
transfer(con, 1, 2, 30)     # Ada 70, Bo 80
transfer(con, 1, 2, 500)    # raises ValueError, balances unchanged
transfer(con, 1, 99, 10)    # raises KeyError(99), Ada still 70
```
