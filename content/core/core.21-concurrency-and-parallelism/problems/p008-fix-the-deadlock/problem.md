# Fix: the bank that freezes

`starter.py` is a tiny bank used by a payment service with many worker threads. Every
`Account` has a `number`, a `balance` and its own `lock`. The function `pause()` stands for a
slow fraud check or a database round-trip; **keep every `pause()` call where it is**, inside
or outside the locks exactly as the comments say. Real systems have such gaps, and they are
what make these bugs show up.

The bug reports:

1. "Two clerks sent money between accounts 1 and 2 at the same moment, one each way. Both
   requests **hang forever**."
2. "`deposit_many([10, 20])` **never returns**, even with only one thread running."
3. "An account with 100 had ten withdrawals of 30 at once. **All ten succeeded** and the
   balance is now -200. At most three should have succeeded."

Fix `starter.py`. Keep the names and parameters. The rules:

- `deposit(amount)` and `withdraw(amount)` change one account under its lock. `withdraw`
  raises `ValueError` if the balance is too small, and then changes nothing.
- `deposit_many(amounts)` deposits every amount while holding the lock **once** (so no other
  thread sees half of the batch).
- `transfer(src, dst, amount)` moves money **atomically**: while it runs, no other thread may
  see the money missing from both accounts or present in both. It raises `ValueError` (and
  changes nothing) if `src` has too little money, and also if `src` and `dst` are the same
  account.
- The total amount of money in the bank never changes because of transfers.

**Example**

```python
a, b = Account(1, 100), Account(2, 100)
transfer(a, b, 30)
print(a.balance, b.balance)        # 70 130
a.deposit_many([10, 20])
print(a.balance)                   # 100
a.withdraw(500)                    # ValueError: insufficient funds
transfer(a, a, 5)                  # ValueError: cannot transfer to the same account
```

The tests run your code in **daemon** threads and give up after a few seconds, so a deadlock
makes a test fail with a message instead of freezing your terminal. (When your own program
freezes, `py-spy dump --pid PID` or `faulthandler.dump_traceback_later(...)` from core.20 show
where every thread is stuck.)
