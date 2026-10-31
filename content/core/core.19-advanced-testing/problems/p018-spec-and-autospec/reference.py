from unittest.mock import create_autospec


def make_bank(bank_class):
    bank = create_autospec(bank_class, instance=True)
    bank.withdraw.return_value = True
    bank.balance.return_value = 100
    return bank


def transfer(bank, src, dst, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if bank.withdraw(src, amount):
        bank.deposit(dst, amount)
        return True
    return False
