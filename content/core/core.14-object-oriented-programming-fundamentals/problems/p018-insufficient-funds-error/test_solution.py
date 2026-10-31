import pytest

from solution import Account, InsufficientFundsError


def test_is_an_exception():
    assert issubclass(InsufficientFundsError, Exception), "InsufficientFundsError must inherit from Exception."
    assert InsufficientFundsError is not Exception, "Make your own class: class InsufficientFundsError(Exception):"


def test_attributes():
    e = InsufficientFundsError(200, 500)
    assert (e.balance, e.amount) == (200, 500), "Store balance and amount on self, in that order of parameters."
    assert e.shortfall == 300, "shortfall is amount - balance: 500 - 200 = 300."


def test_message():
    e = InsufficientFundsError(200, 500)
    assert str(e) == "cannot withdraw 500: balance is only 200", (
        "str(e) should be 'cannot withdraw 500: balance is only 200'. Pass this message to super().__init__()."
    )
    assert e.args == ("cannot withdraw 500: balance is only 200",), (
        "Pass exactly the message to super().__init__(message), so e.args holds just the message."
    )


def test_withdraw_ok():
    acc = Account(200)
    assert acc.withdraw(50) == 150, "withdraw(50) from 200 returns 150."
    assert acc.withdraw(150) == 0, "Withdrawing the whole balance is allowed."


def test_default_balance():
    assert Account().balance == 0, "Account() starts with balance 0."


def test_withdraw_too_much_raises_custom_error():
    acc = Account(200)
    try:
        acc.withdraw(500)
    except InsufficientFundsError as e:
        assert e.balance == 200 and e.amount == 500 and e.shortfall == 300, "Raise InsufficientFundsError(self.balance, amount)."
        assert str(e) == "cannot withdraw 500: balance is only 200", "The message must show the amount and the balance."
    else:
        pytest.fail("withdraw(500) with balance 200 must raise InsufficientFundsError.")
    assert acc.balance == 200, "A failed withdraw must not change the balance. Raise before subtracting."


def test_caught_by_except_exception():
    acc = Account(10)
    with pytest.raises(Exception):
        acc.withdraw(11)


def test_not_caught_by_unrelated_except():
    acc = Account(10)
    with pytest.raises(InsufficientFundsError):
        try:
            acc.withdraw(11)
        except (ValueError, KeyError):
            pytest.fail("InsufficientFundsError should be its own class, not a ValueError or KeyError.")
