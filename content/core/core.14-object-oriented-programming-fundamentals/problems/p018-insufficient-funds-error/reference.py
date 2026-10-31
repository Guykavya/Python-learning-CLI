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
