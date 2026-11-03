## Approach

Validate the cheap things before touching the database. Then do all database work inside `with con:`. Every exception raised inside the block (KeyError for a missing target, after the debit has been executed) makes `with con:` roll back, so the debit disappears. If the block finishes, it commits.

## Code

```python
def transfer(con, source, target, amount):
    if not isinstance(amount, int) or amount <= 0 or source == target:
        raise ValueError("amount must be a positive integer and accounts must differ")
    with con:
        row = con.execute("SELECT balance FROM accounts WHERE id = ?", (source,)).fetchone()
        if row is None:
            raise KeyError(source)
        if row[0] < amount:
            raise ValueError("insufficient funds")
        con.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, source))
        cur = con.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, target))
        if cur.rowcount == 0:
            raise KeyError(target)
```

## Complexity

Three primary-key statements: O(log n) each. The commit (a disk sync) dominates the time.

## Another way / portable SQL

Do the check inside the update itself: `UPDATE accounts SET balance = balance - ? WHERE id = ? AND balance >= ?` and look at `rowcount`; that also avoids a race where another connection changes the balance between your `SELECT` and `UPDATE`.
For real concurrency use `BEGIN IMMEDIATE` (SQLite) or `SELECT ... FOR UPDATE` (PostgreSQL, MySQL). Explicit style: `try: ... con.commit() except: con.rollback(); raise`.
