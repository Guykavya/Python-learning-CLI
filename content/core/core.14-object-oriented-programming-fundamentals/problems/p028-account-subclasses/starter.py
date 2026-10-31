class Account:
    def __init__(self, owner, balance=0):
        # TODO: check the balance, set owner, balance and transactions
        pass

    def deposit(self, amount):
        return 0

    def available(self):
        return 0

    def withdraw(self, amount):
        # TODO: use self.available() for the check
        return 0


class SavingsAccount(Account):
    def __init__(self, owner, balance=0, rate=0.04):
        # TODO: call the parent's __init__, then check and store rate
        pass

    def add_interest(self):
        return 0

    # TODO: override withdraw: count withdrawals, call super().withdraw(amount)


class CheckingAccount(Account):
    def __init__(self, owner, balance=0, overdraft=500):
        pass

    # TODO: override available()
