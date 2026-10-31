from unittest.mock import Mock


def make_bank(bank_class):
    return Mock()


def transfer(bank, src, dst, amount):
    bank.withdraw(src, amount)
    bank.deposit(dst, amount)
    return True
