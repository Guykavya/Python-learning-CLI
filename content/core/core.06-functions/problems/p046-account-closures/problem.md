# A bank account made of closures

Write `make_account(balance=0)` that returns a **dict of three functions** sharing one private
balance:

- `"deposit"`: `deposit(amount)` adds to the balance and returns the new balance. A non-positive
  amount is refused: return `None` and change nothing.
- `"withdraw"`: `withdraw(amount)` subtracts and returns the new balance, or returns `None` and
  changes nothing if the amount is non-positive or more than the balance.
- `"balance"`: `balance()` returns the current balance.

Two accounts must be completely independent. There must be **no global variables**.

**Example**

```python
acct = make_account(100)
acct["deposit"](50)      # 150
acct["withdraw"](30)     # 120
acct["withdraw"](500)    # None
acct["balance"]()        # 120
other = make_account()
other["balance"]()       # 0
```

This is the shape of the module project's "state with functions" idea: no class needed.
