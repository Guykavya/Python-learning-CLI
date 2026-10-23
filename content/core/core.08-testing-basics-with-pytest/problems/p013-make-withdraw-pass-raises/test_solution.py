import pytest

from solution import withdraw


def test_normal_withdrawal():
    assert withdraw(100, 30) == 70, "Return balance - amount."


def test_withdraw_everything_is_allowed():
    assert withdraw(100, 100) == 0, "amount == balance is allowed. Use > (not >=) for the check."


def test_zero_amount_rejected():
    with pytest.raises(ValueError, match="positive"):
        withdraw(100, 0)


def test_negative_amount_rejected():
    with pytest.raises(ValueError, match="positive"):
        withdraw(100, -5)


def test_too_much_rejected():
    with pytest.raises(ValueError, match="insufficient"):
        withdraw(100, 500)


def test_just_over_the_balance_rejected():
    with pytest.raises(ValueError, match="insufficient"):
        withdraw(100, 101)


def test_empty_account_cannot_pay():
    with pytest.raises(ValueError, match="insufficient"):
        withdraw(0, 1)
