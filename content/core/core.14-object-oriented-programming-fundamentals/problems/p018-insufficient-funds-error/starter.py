class InsufficientFundsError(Exception):
    # TODO: __init__(self, balance, amount): message, balance, amount, shortfall
    pass


class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def withdraw(self, amount):
        # TODO: raise InsufficientFundsError when amount > balance
        self.balance -= amount
        return self.balance
