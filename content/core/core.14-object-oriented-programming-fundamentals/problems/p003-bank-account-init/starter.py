class Account:
    def __init__(self, owner, balance=0):
        # TODO: check owner and balance, then store them on self
        pass

    def deposit(self, amount):
        # TODO: check amount, add it, return the new balance
        raise NotImplementedError

    def withdraw(self, amount):
        # TODO: check amount (positive, not too big), take it away, return the new balance
        raise NotImplementedError
