## Approach

A custom exception is an ordinary class that inherits from `Exception` (chapter section 17). Give it
an `__init__` that takes the useful data, stores it as attributes, and passes a readable message up to
`Exception` with `super().__init__(message)` (section 11). `Exception` keeps the message in `args`, and
`str(e)` shows it.

Raising happens **before** the subtraction, so a failed withdraw leaves the account as it was.

## Code

```python
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        super().__init__(f"cannot withdraw {amount}: balance is only {balance}")
        self.balance = balance
        self.amount = amount
        self.shortfall = amount - balance


class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError(self.balance, amount)
        self.balance -= amount
        return self.balance
```

## Complexity

O(1).

## Another way

If you do not need extra attributes, `class InsufficientFundsError(Exception): pass` and
`raise InsufficientFundsError("cannot withdraw ...")` is enough. In a bigger library you would make it
a subclass of your library's base error, for example `class BankError(Exception)` and
`class InsufficientFundsError(BankError)`, so callers can catch every bank problem at once.
