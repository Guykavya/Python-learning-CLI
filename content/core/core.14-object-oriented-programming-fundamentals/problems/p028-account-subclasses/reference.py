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
