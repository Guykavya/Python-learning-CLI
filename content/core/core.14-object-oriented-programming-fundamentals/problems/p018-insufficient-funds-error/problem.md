# A custom exception with extra data

`ValueError("insufficient funds")` tells the caller *that* something failed, but not the numbers.
A custom exception class can carry them as attributes, so the caller can show a good message or
offer "you need 300 more". And `except InsufficientFundsError:` catches exactly this problem and
nothing else.

Write in `solution.py`:

**`InsufficientFundsError`**, a subclass of `Exception`
- `InsufficientFundsError(balance, amount)` stores `balance`, `amount`, and `shortfall`
  (`amount - balance`) as attributes.
- Its message, `str(error)`, is exactly:
  `"cannot withdraw <amount>: balance is only <balance>"`.
  Pass that message to `super().__init__(...)`.

**`Account(balance=0)`**
- Stores `balance`.
- `withdraw(amount)`: if `amount` is more than the balance, raise
  `InsufficientFundsError(self.balance, amount)` and leave the balance unchanged. Otherwise subtract
  it and return the new balance.

**Example**

```python
acc = Account(200)
try:
    acc.withdraw(500)
except InsufficientFundsError as e:
    print(e)              # cannot withdraw 500: balance is only 200
    print(e.shortfall)    # 300
print(acc.balance)        # 200
print(acc.withdraw(50))   # 150
```
