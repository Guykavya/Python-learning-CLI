## Approach

`__init__` is the gate every new object passes through (chapter section 4). If it refuses bad
values, no `Account` with a negative opening balance can ever exist. The methods that change the
object follow the same rule: **check first, change second**. If a check fails, the method raises
before it touches `self.balance`, so the object stays exactly as it was.

In `withdraw`, test "amount must be positive" before "insufficient funds". Otherwise `withdraw(-5)`
passes the funds check (`-5 > balance` is false) and would *add* 5 rupees.

## Code

```python
class Account:
    def __init__(self, owner, balance=0):
        if owner.strip() == "":
            raise ValueError("owner must not be empty")
        if balance < 0:
            raise ValueError("opening balance cannot be negative")
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        return self.balance
```

## Complexity

O(1) for every method.

## Another way

Both methods share the "amount must be positive" check. You can move it into a small helper method
`_check_amount(self, amount)` and call it from both; the leading underscore says "internal"
(section 7). In section 8 you will make `balance` a read-only property, so outside code cannot write
`acc.balance = -1000` and skip all your checks. In section 17 you will replace the plain
`ValueError` with your own exception class.
