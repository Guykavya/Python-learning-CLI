## Approach

**Shared code in the base class.** A savings account and a checking account *are* accounts (an
"is-a" relation), so inheritance fits (chapter section 10). `Account` holds everything they share:
the attributes, `deposit`, `withdraw` and the transaction list. The subclasses add only their
differences.

**`super().__init__` first.** Each subclass `__init__` calls `super().__init__(owner, balance)`.
That runs the parent's checks and creates `owner`, `balance` and `transactions`. Then the subclass
stores its own extra value (section 11).

**A hook method.** `Account.withdraw` does not compare with `self.balance` directly; it asks
`self.available()`. Because Python looks up `available` on the **object's** class first, a
`CheckingAccount` answers with its own version: the parent's answer plus the overdraft. The parent's
`withdraw` never changes, yet it behaves differently for a checking account. This is the template
method idea (section 10).

**Extending a method.** `SavingsAccount.withdraw` adds one rule in front of the parent's work and
one line after it. `super().withdraw(amount)` raises if it fails, so the count is increased only
for a successful withdrawal.

## Code

```python
class Account:
    def __init__(self, owner, balance=0):
        if not isinstance(balance, (int, float)) or balance < 0:
            raise ValueError(f"opening balance must be 0 or more, got {balance!r}")
        self.owner = owner
        self.balance = balance
        self.transactions = []

    def _record(self, kind, amount):
        self.transactions.append((kind, amount))

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be above 0")
        self.balance += amount
        self._record("deposit", amount)
        return self.balance

    def available(self):
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be above 0")
        if amount > self.available():
            raise ValueError("insufficient funds")
        self.balance -= amount
        self._record("withdraw", amount)
        return self.balance


class SavingsAccount(Account):
    MAX_WITHDRAWALS = 3

    def __init__(self, owner, balance=0, rate=0.04):
        super().__init__(owner, balance)
        if not 0 <= rate <= 0.2:
            raise ValueError(f"rate must be between 0 and 0.2, got {rate!r}")
        self.rate = rate
        self._withdrawals = 0

    def add_interest(self):
        interest = round(self.balance * self.rate, 2)
        self.balance = round(self.balance + interest, 2)
        self._record("interest", interest)
        self._withdrawals = 0
        return interest

    def withdraw(self, amount):
        if self._withdrawals >= self.MAX_WITHDRAWALS:
            raise ValueError("withdrawal limit reached")
        new_balance = super().withdraw(amount)   # raises on failure, so the count below is skipped
        self._withdrawals += 1
        return new_balance


class CheckingAccount(Account):
    def __init__(self, owner, balance=0, overdraft=500):
        super().__init__(owner, balance)
        if overdraft < 0:
            raise ValueError(f"overdraft must be 0 or more, got {overdraft!r}")
        self.overdraft = overdraft

    def available(self):
        return super().available() + self.overdraft
```

`MAX_WITHDRAWALS` is a class attribute: one number shared by all savings accounts, read through
`self` (section 5).

## Complexity

Every method is O(1).

## Another way

`CheckingAccount` could override `withdraw` completely and repeat the checks with
`self.balance + self.overdraft`. It works, but now two copies of the withdraw logic must be kept in
step, and a later change to `Account.withdraw` (say, a daily limit) would silently skip checking
accounts. Overriding the small hook keeps one copy of the logic.
