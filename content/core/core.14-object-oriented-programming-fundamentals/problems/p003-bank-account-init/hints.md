## Hint 1

In which order should a method work: change the balance and then check, or check and then change?
What is the balance after a failed call if you change it first?

## Hint 2

`owner.strip() == ""` is `True` for `""` and for `"   "`. A guard is an `if` that raises before
any attribute is changed. `withdraw` needs two guards; which one should come first, so that
`withdraw(-5)` says "amount must be positive" and not "insufficient funds"?

## Hint 3

```
class Account:
    def __init__(self, owner, balance=0):
        if owner is blank: raise ValueError("owner must not be empty")
        if balance < 0:    raise ValueError("opening balance cannot be negative")
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0: raise ValueError("amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount <= 0: raise ...
        if amount > self.balance: raise ValueError("insufficient funds")
        self.balance -= amount
        return self.balance
```
