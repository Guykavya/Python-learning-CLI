def transfer(db, src, dst, paise):
    # TODO: validate; one transaction (with db:) with a checked debit and a credit; raise on failure
    db.execute("UPDATE accounts SET balance_paise = balance_paise - ? WHERE id = ?", (paise, src))
    db.commit()
    db.execute("UPDATE accounts SET balance_paise = balance_paise + ? WHERE id = ?", (paise, dst))
    db.commit()
