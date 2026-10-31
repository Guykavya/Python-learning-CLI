from unittest.mock import create_autospec

import pytest

from solution import make_bank, transfer


class Bank:
    def withdraw(self, account, amount):
        raise RuntimeError("real bank")

    def deposit(self, account, amount):
        raise RuntimeError("real bank")

    def balance(self, account):
        raise RuntimeError("real bank")


def test_make_bank_defaults():
    bank = make_bank(Bank)
    assert bank.withdraw("a", 5) is True, "make_bank must set withdraw.return_value = True."
    assert bank.balance("a") == 100, "make_bank must set balance.return_value = 100."


def test_unknown_attribute_is_an_error():
    bank = make_bank(Bank)
    with pytest.raises(AttributeError):
        bank.widthdraw("a", 5)


def test_wrong_signature_is_an_error():
    bank = make_bank(Bank)
    with pytest.raises(TypeError):
        bank.deposit("a")  # amount missing
    with pytest.raises(TypeError):
        bank.withdraw("a", 5, 6)


def test_mock_looks_like_a_bank_object():
    bank = make_bank(Bank)
    assert isinstance(bank, Bank), (
        "Use create_autospec(bank_class, instance=True): then the mock passes isinstance(bank, Bank).")


def test_transfer_success():
    bank = create_autospec(Bank, instance=True)
    bank.withdraw.return_value = True
    assert transfer(bank, "a", "b", 50) is True, "A successful transfer returns True."
    bank.withdraw.assert_called_once_with("a", 50)
    bank.deposit.assert_called_once_with("b", 50)


def test_transfer_refused_deposits_nothing():
    bank = create_autospec(Bank, instance=True)
    bank.withdraw.return_value = False
    assert transfer(bank, "a", "b", 50) is False, "A refused withdrawal means transfer returns False."
    bank.deposit.assert_not_called()


@pytest.mark.parametrize("amount", [0, -5])
def test_transfer_rejects_non_positive_amounts_before_calling_the_bank(amount):
    bank = create_autospec(Bank, instance=True)
    with pytest.raises(ValueError):
        transfer(bank, "a", "b", amount)
    assert bank.mock_calls == [], "Validate the amount first: the bank must not be called at all."
