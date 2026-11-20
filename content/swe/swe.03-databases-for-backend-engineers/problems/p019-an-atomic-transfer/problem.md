# An atomic transfer

Chapter section 6.2. Money moves between two accounts: debit one, credit the other. Either **both** changes happen or **neither**. Table:

```sql
CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance_paise INTEGER NOT NULL CHECK (balance_paise >= 0));
```

Write `transfer(db, src, dst, paise)` for a `sqlite3` connection `db`:

- It moves `paise` from account `src` to account `dst` inside **one transaction** (use `with db:`: it commits on success and rolls back on an exception).
- `paise <= 0` or `src == dst` raises `ValueError` (before touching anything).
- If `src` does not have enough money, raise `ValueError` (message containing `insufficient`); balances stay unchanged.
- If `src` or `dst` does not exist, raise `LookupError`; balances stay unchanged. In particular, if `dst` is missing the **debit already done must be undone**.
- On success both balances change by exactly `paise`; the sum of all balances never changes.

## Example

```python
# accounts: 1 -> 1000, 2 -> 500
transfer(db, 1, 2, 300)     # balances: 700, 800
transfer(db, 1, 2, 5000)    # ValueError: insufficient funds; still 700, 800
transfer(db, 1, 99, 100)    # LookupError; account 1 is still 700
```
