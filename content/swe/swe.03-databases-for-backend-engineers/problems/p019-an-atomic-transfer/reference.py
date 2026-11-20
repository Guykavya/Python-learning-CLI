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
