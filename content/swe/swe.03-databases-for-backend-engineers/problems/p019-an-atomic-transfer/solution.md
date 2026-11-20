## Approach

```python
def transfer(db, src, dst, paise):
    if paise <= 0:
        raise ValueError("the amount must be positive")
    if src == dst:
        raise ValueError("source and destination must differ")
    with db:                                           # commit on success, rollback on any exception
        cur = db.execute("UPDATE accounts SET balance_paise = balance_paise - ? WHERE id = ? AND balance_paise >= ?",
                         (paise, src, paise))
        if cur.rowcount == 0:
            exists = db.execute("SELECT 1 FROM accounts WHERE id = ?", (src,)).fetchone()
            raise ValueError("insufficient funds") if exists else LookupError(f"no account {src}")
        cur = db.execute("UPDATE accounts SET balance_paise = balance_paise + ? WHERE id = ?", (paise, dst))
        if cur.rowcount == 0:
            raise LookupError(f"no account {dst}")     # the debit above is rolled back
```

The first `UPDATE` both checks and debits in one statement (`AND balance_paise >= ?`), so there is no gap between "enough money?" and "take it". `rowcount` tells whether a row matched. The exceptions are raised **inside** `with db:`, so the connection rolls back everything done so far, including the debit when the credit target is missing. Without the transaction, the money would leave `src` and arrive nowhere.

Example: `transfer(db, 1, 99, 100)`: the debit succeeds (rowcount 1), the credit finds no account 99 (rowcount 0), `LookupError` is raised, `with db:` rolls back: account 1 is back to its old balance.

## Complexity

`O(1)` statements.

## Another way

Check first with a `SELECT`, then update: it works in a single-user program and has a gap in which another connection can spend the money (problem 24).

## Why it matters

This is the textbook case for transactions: the invariant "total money is constant" is true before and after, and never half-broken for anyone else.
