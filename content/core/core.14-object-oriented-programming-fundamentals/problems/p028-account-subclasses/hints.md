## Hint 1

What is the **same** in all three accounts, and what is different? Put everything that is the same
in `Account`. A subclass should contain only its differences. In each subclass `__init__`, what
must happen first so that `owner`, `balance` and `transactions` exist?

## Hint 2

`Account.withdraw` asks `self.available()`, not `self.balance`. When `self` is a
`CheckingAccount`, which `available` runs? So a checking account needs only a new `available()`;
`withdraw` itself stays in the parent. For the savings limit: should you count the withdrawal
before or after `super().withdraw(amount)` has succeeded?

## Hint 3

```
class SavingsAccount(Account):
    __init__(owner, balance, rate):
        super().__init__(owner, balance)
        check 0 <= rate <= 0.2; self.rate = rate; self._withdrawals = 0
    withdraw(amount):
        if self._withdrawals >= 3: raise ValueError("withdrawal limit reached")
        new = super().withdraw(amount)     # raises if it fails
        self._withdrawals += 1
        return new

class CheckingAccount(Account):
    available():
        return super().available() + self.overdraft
```
