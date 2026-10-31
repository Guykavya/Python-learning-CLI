import sqlite3


def open_bank(path, accounts):
    conn = sqlite3.connect(path)
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS accounts ("
            " name TEXT PRIMARY KEY,"
            " balance INTEGER NOT NULL CHECK (balance >= 0))"
        )
        conn.executemany("INSERT INTO accounts (name, balance) VALUES (?, ?)", list(accounts.items()))
    return conn


def balance(conn, name):
    row = conn.execute("SELECT balance FROM accounts WHERE name = ?", (name,)).fetchone()
    if row is None:
        raise KeyError(name)
    return row[0]


def transfer(conn, src, dst, amount):
    if type(amount) is not int or amount <= 0:
        raise ValueError(f"amount must be a positive int, got {amount!r}")
    if src == dst:
        raise ValueError("cannot transfer to the same account")
    try:
        with conn:                                   # one transaction: all or nothing
            cur = conn.execute(
                "UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, src)
            )
            if cur.rowcount == 0:
                raise KeyError(src)
            cur = conn.execute(
                "UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, dst)
            )
            if cur.rowcount == 0:
                raise KeyError(dst)                  # leaving the block with an error rolls back
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"insufficient funds in {src!r}") from exc


def accounts_with_prefix(conn, prefix):
    rows = conn.execute(
        "SELECT name FROM accounts WHERE substr(name, 1, ?) = ? ORDER BY name",
        (len(prefix), prefix),
    )
    return [row[0] for row in rows]
