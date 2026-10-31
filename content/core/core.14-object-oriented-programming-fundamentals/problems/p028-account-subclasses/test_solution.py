import pytest

from solution import Account, CheckingAccount, SavingsAccount


def test_account_basics():
    a = Account("Asha", 100)
    assert (a.owner, a.balance, a.transactions) == ("Asha", 100, []), "Set owner, balance and an empty transactions list."
    assert a.deposit(50) == 150, "deposit returns the new balance."
    assert a.withdraw(30) == 120, "withdraw returns the new balance."
    assert a.transactions == [("deposit", 50), ("withdraw", 30)], "Record each change as (kind, amount)."
    assert Account("Zoya").balance == 0, "balance defaults to 0."


def test_account_errors():
    with pytest.raises(ValueError):
        Account("X", -1)
    a = Account("Asha", 100)
    for bad in (0, -5):
        with pytest.raises(ValueError):
            a.deposit(bad)
        with pytest.raises(ValueError):
            a.withdraw(bad)
    with pytest.raises(ValueError, match="insufficient funds"):
        a.withdraw(101)
    assert a.balance == 100 and a.transactions == [], "Failed calls must not change the balance or the transactions."


def test_transactions_not_shared():
    a = Account("A")
    b = Account("B")
    a.deposit(10)
    assert b.transactions == [], "Each account needs its own list: create it in __init__ with self.transactions = []."


def test_subclasses_are_accounts():
    assert isinstance(SavingsAccount("R"), Account), "SavingsAccount must inherit from Account."
    assert isinstance(CheckingAccount("M"), Account), "CheckingAccount must inherit from Account."


def test_subclass_init_calls_super():
    s = SavingsAccount("Ravi", 1000, rate=0.05)
    assert (s.owner, s.balance, s.transactions, s.rate) == ("Ravi", 1000, [], 0.05), (
        "SavingsAccount.__init__ must call super().__init__(owner, balance) and then store rate."
    )
    c = CheckingAccount("Meera", 200, overdraft=300)
    assert (c.owner, c.balance, c.transactions, c.overdraft) == ("Meera", 200, [], 300), (
        "CheckingAccount.__init__ must call super().__init__(owner, balance) and then store overdraft."
    )
    assert SavingsAccount("R").rate == 0.04 and CheckingAccount("M").overdraft == 500, "Check the default rate and overdraft."


def test_subclass_init_validation():
    with pytest.raises(ValueError):
        SavingsAccount("R", -5)
    for rate in (-0.01, 0.21):
        with pytest.raises(ValueError):
            SavingsAccount("R", 100, rate=rate)
    assert SavingsAccount("R", 100, rate=0.2).rate == 0.2, "0.2 itself is allowed."
    with pytest.raises(ValueError):
        CheckingAccount("M", 100, overdraft=-1)
    with pytest.raises(ValueError):
        CheckingAccount("M", -1)


def test_add_interest():
    s = SavingsAccount("Ravi", 1000, rate=0.05)
    assert s.withdraw(100) == 900, "A savings withdrawal works like a normal one."
    assert s.add_interest() == 45.0, "Interest is round(900 * 0.05, 2) = 45.0."
    assert s.balance == 945.0, "The interest is added to the balance."
    assert s.transactions == [("withdraw", 100), ("interest", 45.0)], "Record the interest as ('interest', 45.0)."
    s2 = SavingsAccount("Ravi", 333.33, rate=0.03)
    assert s2.add_interest() == 10.0, "round(333.33 * 0.03, 2) is 10.0."
    assert s2.balance == 343.33, "Round the new balance to 2 decimals."


def test_savings_withdrawal_limit():
    s = SavingsAccount("Ravi", 1000)
    for _ in range(3):
        s.withdraw(10)
    with pytest.raises(ValueError, match="limit"):
        s.withdraw(10)
    assert s.balance == 970, "The refused 4th withdrawal must not change the balance."
    s.add_interest()
    s.withdraw(10)
    assert len([t for t in s.transactions if t[0] == "withdraw"]) == 4, "add_interest starts a new period: withdrawing works again."


def test_failed_withdrawal_does_not_count():
    s = SavingsAccount("Ravi", 50)
    for _ in range(3):
        with pytest.raises(ValueError, match="insufficient"):
            s.withdraw(100)
    try:
        result = s.withdraw(10)
    except ValueError:
        pytest.fail(
            "Failed withdrawals must not count toward the limit. Increase the count only after super().withdraw succeeds."
        )
    assert result == 40, "50 - 10 = 40."


def test_savings_cannot_go_negative():
    s = SavingsAccount("Ravi", 50)
    with pytest.raises(ValueError, match="insufficient"):
        s.withdraw(51)


def test_checking_overdraft():
    c = CheckingAccount("Meera", 200, overdraft=300)
    assert c.available() == 500, "available() for a checking account is balance + overdraft (use super().available())."
    try:
        result = c.withdraw(450)
    except ValueError:
        pytest.fail(
            "A checking account may go below 0, down to -overdraft. Account.withdraw must compare with "
            "self.available(), and CheckingAccount.available() adds the overdraft."
        )
    assert result == -250, "200 - 450 = -250."
    assert c.available() == 50, "Only 50 more is available at -250 with an overdraft of 300."
    with pytest.raises(ValueError, match="insufficient funds"):
        c.withdraw(100)
    assert c.balance == -250, "The refused withdrawal must not change the balance."
    assert c.withdraw(50) == -300, "Withdrawing exactly down to -overdraft is allowed."
    assert c.deposit(300) == 0, "deposit is inherited unchanged."
    assert c.transactions == [("withdraw", 450), ("withdraw", 50), ("deposit", 300)], "Transactions are recorded as in Account."


def test_checking_has_no_limit_on_count():
    c = CheckingAccount("Meera", 100)
    for _ in range(5):
        c.withdraw(1)
    assert c.balance == 95, "The 3-withdrawal limit belongs to SavingsAccount only."


def test_basic_account_available():
    a = Account("Asha", 70)
    assert a.available() == 70, "For a basic account available() is the balance."
