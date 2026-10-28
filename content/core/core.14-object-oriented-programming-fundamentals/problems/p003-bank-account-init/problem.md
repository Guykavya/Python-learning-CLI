# A bank account that checks its input

An object should never be in a state that makes no sense. A bank account with a balance of
`-500` that nobody borrowed is such a state. The best place to stop it is `__init__` and the
methods that change the object: check first, change second.

Write a class `Account` in `solution.py`:

- `Account(owner, balance=0)` stores `owner` and `balance` as attributes.
  - If `owner` is an empty string (or only spaces), raise `ValueError("owner must not be empty")`.
  - If `balance` is negative, raise `ValueError("opening balance cannot be negative")`.
- `acc.deposit(amount)` adds `amount` to the balance and **returns the new balance**.
  If `amount` is zero or negative, raise `ValueError("amount must be positive")`.
- `acc.withdraw(amount)` takes `amount` away and **returns the new balance**.
  - If `amount` is zero or negative, raise `ValueError("amount must be positive")`.
  - If `amount` is bigger than the balance, raise `ValueError("insufficient funds")`.
- A call that raises must leave the balance **unchanged**.

Amounts are whole rupees (`int`).

**Example**

```python
acc = Account("Kavya")
print(acc.owner, acc.balance)   # Kavya 0
print(acc.deposit(500))         # 500
print(acc.withdraw(120))        # 380
acc.withdraw(1000)              # ValueError: insufficient funds
print(acc.balance)              # 380   (unchanged)
Account("Ravi", -5)             # ValueError: opening balance cannot be negative
```
