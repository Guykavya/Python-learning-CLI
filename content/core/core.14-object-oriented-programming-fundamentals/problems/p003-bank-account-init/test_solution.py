import pytest

from solution import Account


def test_default_balance_is_zero():
    acc = Account("Kavya")
    assert acc.owner == "Kavya", "Store the owner on self: self.owner = owner."
    assert acc.balance == 0, "With no balance given, the default is 0. Use balance=0 in the def line."


def test_opening_balance():
    acc = Account("Ravi", 250)
    assert acc.balance == 250, "Account('Ravi', 250) should start with balance 250."


def test_zero_opening_balance_is_fine():
    assert Account("Asha", 0).balance == 0, "0 is not negative, so an opening balance of 0 is allowed. Use balance < 0, not <= 0."


def test_negative_opening_balance_raises():
    with pytest.raises(ValueError, match="opening balance cannot be negative"):
        Account("Ravi", -5)


def test_empty_owner_raises():
    with pytest.raises(ValueError, match="owner must not be empty"):
        Account("")
    with pytest.raises(ValueError, match="owner must not be empty"):
        Account("   ")


def test_deposit_returns_new_balance():
    acc = Account("Kavya")
    assert acc.deposit(500) == 500, "deposit(500) on an empty account should return the new balance, 500."
    assert acc.deposit(25) == 525, "A second deposit adds to the balance: 500 + 25 = 525."
    assert acc.balance == 525, "deposit must change self.balance, not only return a number."


def test_withdraw_returns_new_balance():
    acc = Account("Kavya", 500)
    assert acc.withdraw(120) == 380, "withdraw(120) from 500 should return 380."
    assert acc.balance == 380, "withdraw must change self.balance."


def test_withdraw_everything_is_allowed():
    acc = Account("Kavya", 100)
    assert acc.withdraw(100) == 0, "Taking out exactly the whole balance is allowed. Raise only when amount > balance."


@pytest.mark.parametrize("bad", [0, -10])
def test_deposit_non_positive_raises_and_keeps_balance(bad):
    acc = Account("Kavya", 50)
    with pytest.raises(ValueError, match="amount must be positive"):
        acc.deposit(bad)
    assert acc.balance == 50, "A failed deposit must not change the balance. Check before you change."


def test_withdraw_too_much_raises_and_keeps_balance():
    acc = Account("Kavya", 380)
    with pytest.raises(ValueError, match="insufficient funds"):
        acc.withdraw(1000)
    assert acc.balance == 380, "A failed withdraw must leave the balance unchanged. Check first, then subtract."


@pytest.mark.parametrize("bad", [0, -5])
def test_withdraw_non_positive_raises(bad):
    acc = Account("Kavya", 380)
    try:
        acc.withdraw(bad)
    except ValueError as e:
        assert "amount must be positive" in str(e), (
            f"withdraw({bad}) should say 'amount must be positive'. Check amount <= 0 BEFORE the funds check."
        )
    else:
        pytest.fail(f"withdraw({bad}) must raise ValueError('amount must be positive'). Did you forget the amount <= 0 check?")
    assert acc.balance == 380, "withdraw(-5) must not ADD 5 to the balance. Reject zero and negative amounts first."


def test_accounts_are_independent():
    a = Account("A", 10)
    b = Account("B", 10)
    a.deposit(5)
    assert b.balance == 10, "Each account has its own balance. Store it on self, not on the class."
