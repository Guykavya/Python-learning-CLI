class BankError(Exception):
    pass


# TODO: AccountNotFound, InsufficientFunds, AccountFrozen, TransferError


class Account:
    def __init__(self, account_id, owner, balance=0):
        # TODO
        pass


class Bank:
    def __init__(self):
        # TODO
        pass

    def open(self, account_id, owner, balance=0):
        # TODO
        pass

    def get(self, account_id):
        # TODO
        pass

    def transfer(self, source_id, target_id, amount):
        # TODO
        pass

    def statement(self):
        # TODO
        return []
