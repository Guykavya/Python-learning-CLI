# Bank transfers: transactions, rollback and SQL injection

Two things go wrong in almost every first database program. Both are shown below with real output
from an in-memory database holding `asha 100`, `ravi 50`, `zoya 10`.

**1. SQL injection.** The search builds its SQL with an f-string:

```python
def find_unsafe(conn, prefix):
    sql = f"SELECT name FROM accounts WHERE name LIKE '{prefix}%' ORDER BY name"
    return [row[0] for row in conn.execute(sql)]

find_unsafe(conn, "as")                    # ['asha']
find_unsafe(conn, "nobody' OR 1=1 --")     # ['asha', 'ravi', 'zoya']
```

The second "prefix" closes the quote, adds `OR 1=1` (always true) and comments out the rest with
`--`: the user rewrote your query and sees every account.

**2. Half-done work.** A transfer is *two* updates. If the second one fails, the first must be undone:

```python
conn.execute("UPDATE accounts SET balance = balance - 30 WHERE name = 'asha'")
cur = conn.execute("UPDATE accounts SET balance = balance + 30 WHERE name = 'rahul'")   # typo
cur.rowcount        # 0: nobody received the money
conn.commit()
# [('asha', 70), ('ravi', 50), ('zoya', 10)]      30 rupees vanished
```

A **transaction** groups statements so that either all of them are saved (`commit`) or none
(`rollback`). In Python, `with conn:` commits when the block ends normally and **rolls back** when an
exception leaves it. Also, the table has `CHECK (balance >= 0)`, so the database itself refuses an
overdraft:

```text
IntegrityError: CHECK constraint failed: balance >= 0
```

## Your task

Write in `solution.py`:

1. `open_bank(path, accounts) -> sqlite3.Connection`: connect to `path` (a file or `":memory:"`),
   create `accounts(name TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0))` if it does
   not exist, insert the `accounts` dict (`{"asha": 100, ...}`) with `executemany`, commit, return the
   connection.
2. `balance(conn, name) -> int`. Unknown name: `KeyError`.
3. `transfer(conn, src, dst, amount)`: move `amount` from `src` to `dst` **atomically**.
   - `amount` must be an `int` greater than 0, and `src != dst`; otherwise `ValueError` (check
     before touching the database).
   - Not enough money: `ValueError` (catch the `IntegrityError` from the `CHECK`).
   - `src` or `dst` does not exist (`rowcount == 0`): `KeyError`.
   - After **any** error, no balance has changed and the change is not half-committed. After success the
     change is committed (another connection to the same file sees it).
4. `accounts_with_prefix(conn, prefix) -> list[str]`: account names that start with `prefix`
   (case-sensitive, characters such as `%`, `_` and `'` have no special meaning), sorted. Use
   parameters: SQLite's `substr(name, 1, ?) = ?` compares the first characters of the name exactly.

**Example**

```python
conn = open_bank(":memory:", {"asha": 100, "ravi": 50, "zoya": 10})
transfer(conn, "asha", "ravi", 30)
balance(conn, "asha"), balance(conn, "ravi")     # (70, 80)
transfer(conn, "zoya", "asha", 500)              # ValueError: insufficient funds
transfer(conn, "asha", "rahul", 10)              # KeyError: 'rahul'
balance(conn, "asha")                            # 70    the debit was rolled back
accounts_with_prefix(conn, "nobody' OR 1=1 --")  # []
```
