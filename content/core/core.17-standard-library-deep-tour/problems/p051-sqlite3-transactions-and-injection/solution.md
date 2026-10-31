## Approach

**Atomicity.** Both updates run inside one `with conn:` block. Python's sqlite3 opens a transaction
before the first `UPDATE`; when the block ends normally it commits, and when *any* exception leaves
the block it rolls back. So every failure path simply **raises inside the block**:

- the `CHECK (balance >= 0)` constraint raises `IntegrityError` on an overdraft;
- a missing account is detected with `cur.rowcount == 0` and we raise `KeyError` ourselves.

The rollback happens before the exception reaches the `except`, which only changes its type. Letting
the database enforce "no negative balance" is safer than a `SELECT` followed by an `UPDATE` in
Python: the rule holds for every program that uses the file.

**Injection.** Every value is a `?` parameter; the SQL text never changes. For the prefix,
`substr(name, 1, len) = prefix` compares characters exactly, so `%`, `_` and `'` are ordinary
characters (with `LIKE`, `%` and `_` are wildcards even when passed as parameters).

## Code

```python
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
        with conn:
            cur = conn.execute(
                "UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, src)
            )
            if cur.rowcount == 0:
                raise KeyError(src)
            cur = conn.execute(
                "UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, dst)
            )
            if cur.rowcount == 0:
                raise KeyError(dst)
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"insufficient funds in {src!r}") from exc


def accounts_with_prefix(conn, prefix):
    rows = conn.execute(
        "SELECT name FROM accounts WHERE substr(name, 1, ?) = ? ORDER BY name",
        (len(prefix), prefix),
    )
    return [row[0] for row in rows]
```

## Complexity

Each transfer is two primary-key updates: O(log n). The prefix search scans the table: O(n) plus
sorting the matches.

## Another way

You can manage the transaction by hand: `conn.execute("BEGIN")`, then the updates, then
`conn.commit()` in the success path and `conn.rollback()` in an `except` block that re-raises. The
`with conn:` form does exactly that with less room for mistakes. For a `LIKE` search with a literal
prefix, escape the wildcards yourself (`prefix.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")`)
and add `ESCAPE '\'` to the SQL; note that `LIKE` is also case-insensitive for ASCII letters.
