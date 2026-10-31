## Hint 1

An exception class is a normal class. Its `__init__` can take any parameters you like and store
them on `self`. But who builds the message that `print(e)` shows? What does the base class
`Exception` need to receive for `str(e)` to work?

## Hint 2

```
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        super().__init__(f"cannot withdraw {amount}: balance is only {balance}")
        self.balance = balance
        self.amount = amount
        self.shortfall = amount - balance

class Account:
    withdraw(self, amount):
        if amount > self.balance: raise InsufficientFundsError(self.balance, amount)
        self.balance -= amount
        return self.balance
```
