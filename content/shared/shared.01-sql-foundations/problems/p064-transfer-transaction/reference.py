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
