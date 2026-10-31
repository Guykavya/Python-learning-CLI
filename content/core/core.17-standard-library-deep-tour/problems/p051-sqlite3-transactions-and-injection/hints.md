## Hint 1

Which statements of a transfer must succeed or fail **together**? What does `with conn:` do when an
exception is raised inside it? How do you find out that an `UPDATE ... WHERE name = ?` matched no row?

## Hint 2

Validate `amount` and `src != dst` first (`type(amount) is not int` refuses floats and strings).
Then, inside one `with conn:` block, run the debit, check `cur.rowcount`, run the credit, check
`cur.rowcount`, and `raise KeyError(...)` **inside the block** when a row is missing, so the block
rolls back. Wrap the whole `with` in `try/except sqlite3.IntegrityError` to turn the `CHECK` failure
into `ValueError`.

## Hint 3

```
transfer(conn, src, dst, amount):
    if amount is not a positive int or src == dst: raise ValueError
    try:
        with conn:
            cur = execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, src))
            if cur.rowcount == 0: raise KeyError(src)
            cur = execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (amount, dst))
            if cur.rowcount == 0: raise KeyError(dst)
    except sqlite3.IntegrityError: raise ValueError("insufficient funds")

accounts_with_prefix: "SELECT name FROM accounts WHERE substr(name, 1, ?) = ? ORDER BY name", (len(prefix), prefix)
```
